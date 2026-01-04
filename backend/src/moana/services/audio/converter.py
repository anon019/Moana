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


class AudioConverter:
    """Audio format converter using ffmpeg."""

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
                "-y",
                "-i", str(wav_path),
                "-c:a", "aac",
                "-b:a", bitrate,
                "-movflags", "+faststart",
                str(aac_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

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
