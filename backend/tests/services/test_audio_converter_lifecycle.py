"""使用真实子进程验证转换取消后不会残留后台工作。"""
import asyncio
import io
import shutil
import sys
import wave

import pytest

from moana.services.audio import converter


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", ["timeout", "cancel"])
async def test_conversion_stops_child_on_timeout_or_cancel(monkeypatch, reason):
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-c",
        "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        "print('ready',flush=True); time.sleep(60)",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await process.stdout.readline()
    monkeypatch.setattr(converter, "CONVERSION_TIMEOUT_SECONDS", 0.05 if reason == "timeout" else 10)
    monkeypatch.setattr(converter, "PROCESS_STOP_TIMEOUT_SECONDS", 0.05)
    task = asyncio.create_task(converter._communicate_bounded(process))
    try:
        if reason == "cancel":
            await asyncio.sleep(0.01)
            task.cancel()
        with pytest.raises(asyncio.TimeoutError if reason == "timeout" else asyncio.CancelledError):
            await task
        assert process.returncode is not None
    finally:
        if process.returncode is None:
            process.kill()
            await process.communicate()


@pytest.mark.asyncio
@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="需要 ffmpeg")
@pytest.mark.parametrize("method", ["wav_to_mp3", "wav_to_aac"])
async def test_successful_conversion_still_returns_audio(method):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x00\x00" * 1600)
    result = await getattr(converter.AudioConverter, method)(buffer.getvalue())
    assert len(result) > 100
