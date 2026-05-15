import json
import logging
import time
from groq import AsyncGroq
from groq import RateLimitError, APIError, BadRequestError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True,
    )
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int = 3000,
        temperature: float = 0.1,
    ) -> tuple[str, int]:
        start = time.time()
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        elapsed_ms = int((time.time() - start) * 1000)
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        logger.info(f"Groq {model}: {elapsed_ms}ms, {tokens} tokens")
        return content, elapsed_ms

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int = 3000,
    ) -> tuple[dict, int]:
        raw, elapsed_ms = await self.complete(system_prompt, user_prompt, model, max_tokens)
        try:
            data = json.loads(raw)
            return data, elapsed_ms
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {raw[:500]}")
            raise ValueError(f"LLM returned invalid JSON: {str(e)}")

    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Groq Whisper.
        IMPORTANT: always sends file as 'audio.ogg' — Groq rejects .oga extension.
        """
        start = time.time()
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        if len(audio_bytes) < 100:
            raise ValueError("Audio fayl juda kichik yoki bo'sh.")

        # CRITICAL: always name the file "audio.ogg" — Groq rejects .oga/.m4a etc.
        transcription = await self.client.audio.transcriptions.create(
            file=("audio.ogg", audio_bytes),
            model="whisper-large-v3",
            response_format="json",  # Returns Transcription object with .text
        )

        elapsed = time.time() - start
        transcript = (transcription.text or "").strip()
        logger.info(
            f"Whisper: transcribed {len(audio_bytes)//1024}KB in {elapsed:.1f}s "
            f"→ {len(transcript)} chars"
        )
        return transcript
