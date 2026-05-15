import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, groq_service):
        self.groq = groq_service

    async def process_voice_message(self, telegram_file, voice_duration: int) -> tuple[str, float]:
        """
        Download voice from Telegram and transcribe via Groq Whisper.

        Args:
            telegram_file: telegram.File object (from bot.get_file())
            voice_duration: voice duration in seconds from the Voice message

        Returns:
            (transcript_text, duration_float)
        """
        tmp_path = None
        try:
            # Always save as .ogg — Groq rejects .oga and other variants
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
                tmp_path = tmp.name

            # Use PTB's native download (reliable, handles auth automatically)
            await telegram_file.download_to_drive(tmp_path)

            file_size = os.path.getsize(tmp_path)
            logger.info(f"Voice downloaded via PTB: {file_size / 1024:.1f}KB → {tmp_path}")

            if file_size < 100:
                raise ValueError("Ovoz fayli juda kichik. Mikrofonni tekshiring.")

            transcript = await self.groq.transcribe_audio(tmp_path)

            if not transcript or len(transcript.strip()) < 5:
                raise ValueError(
                    "Ovozdan matn ajratib bo'lmadi. "
                    "Aniqroq va balandroq gapiring, shovqin kamaytiring."
                )

            # Use Telegram's voice.duration as the authoritative duration
            return transcript.strip(), float(voice_duration)

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    logger.debug(f"Temp file deleted: {tmp_path}")
                except OSError:
                    pass
