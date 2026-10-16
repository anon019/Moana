"""免费 CLI 的路由、拒绝付费、并发与取消边界。"""

import asyncio
from datetime import datetime, timezone
import fcntl
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock
import wave

import pytest

from moana.config import get_settings
from moana.services.tts import cli_worker
from moana.services.tts import fish_cli


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setenv("TTS_CLI_TIMEOUT", "2")
    monkeypatch.setenv("FISH_SPEECH_VOICE_ID", "a" * 32)
    monkeypatch.setenv("FISH_SPEECH_API_KEY", "test-only-key")
    get_settings.cache_clear()
    yield fish_cli.FishFreeCLIService()
    get_settings.cache_clear()


def wav_bytes():
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 1600)
    return output.getvalue()


@pytest.mark.parametrize("text,speed", [(None, 1), ("", 1), (" ", 1), ("a" * 1001, 1),
                                          ("你好", 0), ("你好", True), ("你好", float("nan")),
                                          ("你好", 10 ** 1000)])
async def test_invalid_input_cannot_start_cli(service, text, speed):
    service._generate = AsyncMock()
    with pytest.raises(ValueError):
        await service.synthesize(text, speed=speed)
    service._generate.assert_not_called()


def test_fish_free_expiry_is_hard_boundary():
    assert cli_worker.fish_free_available(datetime(2026, 11, 30, 23, 59, tzinfo=timezone.utc))
    assert not cli_worker.fish_free_available(datetime(2026, 12, 1, tzinfo=timezone.utc))


@pytest.mark.parametrize("voice", ["Kore", "Leda", "Aoede", "Puck", "Charon", "Fenrir"])
def test_legacy_voice_preflight_uses_configured_fish_voice(service, voice):
    assert service.validate_configuration(voice) == "a" * 32


async def test_old_fish_provider_rejects_missing_key_without_network(monkeypatch):
    from moana.services.tts.fish_speech import FishSpeechService
    monkeypatch.setenv("FISH_SPEECH_API_KEY", "")
    get_settings.cache_clear()
    try:
        service = FishSpeechService()
        with pytest.raises(ValueError, match="FISH_SPEECH_API_KEY"):
            await service._generate("你好", 1, None)
    finally:
        get_settings.cache_clear()


async def test_fish_expired_rejects_before_process(monkeypatch):
    service = fish_cli.FishFreeCLIService()
    monkeypatch.setattr(fish_cli, "fish_free_available", lambda: False)
    with pytest.raises(ValueError, match="免费期限已结束"):
        await service._generate("你好", 1, None)


async def test_lock_queue_counts_towards_timeout(service, monkeypatch, tmp_path):
    lock = tmp_path / "lock"
    monkeypatch.setattr(fish_cli, "MEDIA_CLI_LOCK", str(lock))
    service._timeout = 0.05
    service._generate = AsyncMock()
    with lock.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        with pytest.raises(TimeoutError):
            await service.synthesize("你好")
        service._generate.assert_not_called()
    async with fish_cli.media_cli_lock():
        pass


async def test_result_measures_wav_and_reports_configured_fish_voice(service, monkeypatch, tmp_path):
    monkeypatch.setattr(fish_cli, "MEDIA_CLI_LOCK", str(tmp_path / "lock"))
    service._generate = AsyncMock(return_value=wav_bytes())
    monkeypatch.setattr(fish_cli.AudioConverter, "wav_to_mp3", AsyncMock(return_value=b"mp3"))
    storage = SimpleNamespace(upload_bytes=AsyncMock(return_value=SimpleNamespace(
        success=True, url="/media/audio/fish_free/test.mp3")))
    monkeypatch.setattr(fish_cli, "get_storage_service", lambda: storage)
    result = await service.synthesize("你好", voice_id="Kore")
    assert result.duration == 0.1
    assert result.voice_id == "a" * 32
    assert result.model == fish_cli.FishFreeCLIService.MODEL


async def test_storage_failure_does_not_report_empty_url(service, monkeypatch, tmp_path):
    monkeypatch.setattr(fish_cli, "MEDIA_CLI_LOCK", str(tmp_path / "lock"))
    service._generate = AsyncMock(return_value=wav_bytes())
    monkeypatch.setattr(fish_cli.AudioConverter, "wav_to_mp3", AsyncMock(return_value=b"mp3"))
    monkeypatch.setattr(fish_cli, "get_storage_service", lambda: SimpleNamespace(
        upload_bytes=AsyncMock(return_value=SimpleNamespace(success=False, url=None))))
    with pytest.raises(RuntimeError, match="保存失败"):
        await service.synthesize("你好")


async def test_cancellation_kills_entire_process_group(service, monkeypatch, tmp_path):
    service._fish_key = "test-only-key"
    service._python = __import__("sys").executable
    started = asyncio.Event()
    waited = []
    class Process:
        pid = 1234567
        returncode = None
        async def communicate(self, data):
            started.set()
            await asyncio.Event().wait()
        async def wait(self):
            waited.append(True)
            self.returncode = -9
    monkeypatch.setattr(fish_cli.asyncio, "create_subprocess_exec", AsyncMock(return_value=Process()))
    killed = []
    monkeypatch.setattr(fish_cli.os, "killpg", lambda pid, sig: killed.append(pid))
    task = asyncio.create_task(service._generate("你好", 1, "a" * 32))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert killed == [1234567]
    assert waited == [True]


def test_fixed_free_model_header_and_real_audio_response(monkeypatch, tmp_path):
    import json
    monkeypatch.setenv("FISH_SPEECH_API_KEY", "test-only-key")
    requests = []
    def urlopen(request, timeout):
        requests.append(request)
        assert timeout == 60
        return io.BytesIO(wav_bytes())
    monkeypatch.setattr(cli_worker.urllib.request, "build_opener", lambda *args: SimpleNamespace(open=urlopen))
    output = tmp_path / "fish.wav"
    cli_worker.generate_fish("你好", 0.8, output, "a" * 32)
    assert output.read_bytes() == wav_bytes()
    assert len(requests) == 1
    assert requests[0].full_url == "https://api.fish.audio/v1/tts"
    assert requests[0].get_header("Model") == "s2.1-pro-free"
    body = json.loads(requests[0].data)
    assert body["reference_id"] == "a" * 32
    assert body["prosody"] == {"speed": 0.8}
    assert body["format"] == "wav"


def test_fish_error_does_not_retry_or_use_paid_model(monkeypatch, tmp_path):
    from urllib.error import HTTPError
    monkeypatch.setenv("FISH_SPEECH_API_KEY", "test-only-key")
    calls = []
    def fail(request, timeout):
        calls.append(request.get_header("Model"))
        raise HTTPError(request.full_url, 402, "Payment Required", {}, None)
    monkeypatch.setattr(cli_worker.urllib.request, "build_opener", lambda *args: SimpleNamespace(open=fail))
    with pytest.raises(HTTPError):
        cli_worker.generate_fish("你好", 1, tmp_path / "fish.wav", "a" * 32)
    assert calls == ["s2.1-pro-free"]


def test_configuration_can_be_checked_before_images(service):
    assert service.validate_configuration() == "a" * 32
    service._voice_id = ""
    with pytest.raises(ValueError, match="FISH_SPEECH_VOICE_ID"):
        service.validate_configuration()


async def test_unconfigured_voice_list_does_not_advertise_placeholder(service):
    service._voice_id = ""
    assert await service.list_voices() == []


@pytest.mark.parametrize("voice", [[], {}, 123, True])
async def test_non_string_voice_reports_validation_error(service, voice):
    with pytest.raises(ValueError, match="必须为字符串"):
        await service.synthesize("你好", voice_id=voice)
