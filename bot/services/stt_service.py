import logging
import os
import tempfile
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, groq_service):
        self.groq = groq_service

    async def download_voice(self, file_url: str) -> str:
        _, suffix = os.path.splitext(file_url.split("?")[0])
        if not suffix:
            suffix = ".ogg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_path = tmp.name
        tmp.close()

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                resp.raise_for_status()
                async with aiofiles.open(tmp_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        await f.write(chunk)

        file_size = os.path.getsize(tmp_path)
        logger.info(f"Voice downloaded: {tmp_path} ({file_size / 1024:.1f}KB)")
        return tmp_path

    async def process_voice_message(self, file_url: str, bot_token: str = None) -> tuple[str, float]:
        tmp_path = None
        try:
            tmp_path = await self.download_voice(file_url)
            transcript, duration = await self.groq.transcribe_audio(tmp_path)

            if not transcript or len(transcript.strip()) < 5:
                raise ValueError(
                    "Ovozdan matn ajratib bo'lmadi. Aniqroq va balandroq gapiring, shovqin kamaytiring."
                )
            return transcript.strip(), duration
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
