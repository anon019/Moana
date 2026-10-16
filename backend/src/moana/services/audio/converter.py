"""Audio format conversion utilities using ffmpeg.

Note: This module uses asyncio.create_subprocess_exec which is the safe
equivalent of Node.js execFile - it passes arguments as a list without
shell expansion, preventing command injection vulnerabilities.
"""
import asyncio
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

CONVERSION_TIMEOUT_SECONDS = 60
PROCESS_STOP_TIMEOUT_SECONDS = 2


async def _communicate_bounded(process):
    """转换超时或调用方取消时回收子进程，避免后台残留 ffmpeg。"""
    try:
        return await asyncio.wait_for(process.communicate(), CONVERSION_TIMEOUT_SECONDS)
    finally:
        if process.returncode is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(process.communicate(), PROCESS_STOP_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                await process.communicate()


class AudioConverter:
    """Audio format converter using ffmpeg."""

    @staticmethod
    async def wav_to_mp3(
        wav_data: bytes,
        bitrate: str = "64k",
    ) -> bytes:
        """Convert WAV audio to MP3.

        MP3 is widely supported by mini programs and is cached by the CDN by
        default. 64 kbps mono audio is sufficient for short spoken narration.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = Path(wav_file.name)
            wav_file.write(wav_data)

        mp3_path = wav_path.with_suffix(".mp3")

        try:
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-nostdin", "-v", "error",
                "-y",
                "-i", str(wav_path),
                "-map_metadata", "-1",
                "-c:a", "libmp3lame",
                "-b:a", bitrate,
                str(mp3_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await _communicate_bounded(process)

            if process.returncode != 0:
                logger.error(f"ffmpeg failed: {stderr.decode()}")
                raise RuntimeError(f"ffmpeg conversion failed: {stderr.decode()[:200]}")

            mp3_data = mp3_path.read_bytes()
            logger.info(
                f"Converted WAV ({len(wav_data)} bytes) to MP3 ({len(mp3_data)} bytes), "
                f"ratio: {len(mp3_data) / len(wav_data):.1%}"
            )
            return mp3_data

        finally:
            wav_path.unlink(missing_ok=True)
            mp3_path.unlink(missing_ok=True)

    @staticmethod
    async def wav_to_aac(
        wav_data: bytes,
        bitrate: str = "96k",
    ) -> bytes:
        """Convert WAV audio to AAC format.

        Args:
            wav_data: Input WAV audio bytes
            bitrate: Output bitrate (default 96k, suitable for speech)

        Returns:
            AAC audio bytes (in M4A container)

        Raises:
            RuntimeError: If ffmpeg conversion fails
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = Path(wav_file.name)
            wav_file.write(wav_data)

        aac_path = wav_path.with_suffix(".m4a")

        try:
            # Run ffmpeg to convert WAV to AAC
            # Using create_subprocess_exec (safe, no shell expansion)
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-nostdin", "-v", "error",
                "-y",
                "-i", str(wav_path),
                "-c:a", "aac",
                "-b:a", bitrate,
                "-movflags", "+faststart",
                str(aac_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await _communicate_bounded(process)

            if process.returncode != 0:
                logger.error(f"ffmpeg failed: {stderr.decode()}")
                raise RuntimeError(f"ffmpeg conversion failed: {stderr.decode()[:200]}")

            # Read converted file
            aac_data = aac_path.read_bytes()
            logger.info(
                f"Converted WAV ({len(wav_data)} bytes) to AAC ({len(aac_data)} bytes), "
                f"ratio: {len(aac_data) / len(wav_data):.1%}"
            )
            return aac_data

        finally:
            # Cleanup temp files
            wav_path.unlink(missing_ok=True)
            aac_path.unlink(missing_ok=True)
