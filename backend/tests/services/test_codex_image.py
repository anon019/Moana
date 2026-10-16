"""订阅出图只能导入真实位图，不能回退 Google/API 或泄露服务密钥。"""

import asyncio
import io
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

from PIL import Image
import pytest

from moana.services.image.codex import CodexImageService


def bitmap():
    stream = io.BytesIO()
    Image.new("RGB", (64, 64), "blue").save(stream, format="PNG")
    return stream.getvalue()


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_output", [False, True])
async def test_image_cli_preserves_references_and_uses_subscription(monkeypatch, tmp_path, bad_output):
    service = CodexImageService()
    service._isolate = False
    service._home = tmp_path
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/invalid-test-credential")
    original = asyncio.create_subprocess_exec
    data = b"<svg/>" if bad_output else bitmap()
    seen = []

    async def spawn(*args, **kwargs):
        assert 'forced_login_method="chatgpt"' in args
        assert not {"OPENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"} & kwargs["env"].keys()
        assert args[args.index("--model") + 1] == "gpt-6-luna"
        directory = Path(args[args.index("--cd") + 1])
        thread_id = "00000000-0000-0000-0000-000000000001"
        images_dir = Path(kwargs["env"]["CODEX_HOME"]) / "generated_images" / thread_id
        images_dir.mkdir(parents=True)
        reference = Path(args[args.index("--image") + 1])
        assert reference.read_bytes() == bitmap()
        seen.append(directory)
        return await original(
            sys.executable, "-c",
            "import pathlib,sys,json;sys.stdin.read();pathlib.Path(sys.argv[1]).write_bytes(bytes.fromhex(sys.argv[2]));print(json.dumps({'type':'thread.started','thread_id':sys.argv[3]}));print(json.dumps({'type':'turn.completed'}))",
            str(images_dir / "exec-test.png"), data.hex(), thread_id, **kwargs,
        )

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    if bad_output:
        with pytest.raises(Exception, match="cannot identify image"):
            await service.generate_raw("测试插画", reference_images=[(bitmap(), "image/png")])
    else:
        assert await service.generate_raw("测试插画", reference_images=[(bitmap(), "image/png")]) == data
    assert seen and not seen[0].exists()
    assert service.model_name == "not_exposed_by_tool"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.parametrize("isolated", [False, True])
async def test_image_timeout_and_cancel_reap_cli(monkeypatch, cancel, isolated):
    import moana.services.image.codex as module

    service = CodexImageService()
    service._isolate = isolated
    service._stop_unit = AsyncMock()
    monkeypatch.setattr(module, "available_memory_kib", lambda: 512 * 1024)
    service._timeout = 30 if cancel else 0.1
    original = asyncio.create_subprocess_exec
    processes = []

    async def spawn(*args, **kwargs):
        if isolated:
            assert args[0] == "systemd-run"
            assert "MemoryMax=384M" in args and "CPUQuota=50%" in args and "TasksMax=96" in args
        process = await original(sys.executable, "-c", "import time;time.sleep(30)", **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    task = asyncio.create_task(service.generate_raw("测试插画"))
    while not processes:
        await asyncio.sleep(0.001)
    if cancel:
        task.cancel()
    with pytest.raises(asyncio.CancelledError if cancel else TimeoutError):
        await task
    assert processes[0].returncode is not None
    if isolated:
        service._stop_unit.assert_awaited_once()


@pytest.mark.asyncio
async def test_real_bitmap_storage_records_actual_dimensions(monkeypatch):
    import moana.services.storage as storage_module

    service = CodexImageService()
    service.generate_raw = AsyncMock(return_value=bitmap())
    uploads = []

    async def upload(data, key, content_type):
        with Image.open(io.BytesIO(data)) as image:
            assert image.format == "WEBP"
        uploads.append(key)
        return SimpleNamespace(success=True, url="/media/" + key)

    monkeypatch.setattr(storage_module, "get_storage_service", lambda: SimpleNamespace(upload_bytes=upload))
    result = await service.generate("测试插画")
    assert (result.width, result.height) == (64, 64)
    assert result.model == "not_exposed_by_tool"
    assert result.url == "/media/image.webp" and result.thumb_url == "/media/thumb.webp"
    assert len(uploads) == 2


@pytest.mark.asyncio
async def test_queue_timeout_never_starts_cli(monkeypatch, tmp_path):
    import fcntl
    import moana.services.image.codex as module

    path = str(tmp_path / "lock")
    monkeypatch.setattr(module, "MEDIA_CLI_LOCK", path)
    service = CodexImageService()
    service._timeout = 0.02

    async def unexpected(*args, **kwargs):
        pytest.fail("排队超时不得启动模型请求")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", unexpected)
    with open(path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(TimeoutError):
            await service.generate_raw("测试插画")


@pytest.mark.asyncio
async def test_low_memory_prevents_starting_model_worker(monkeypatch):
    import moana.services.image.codex as module

    service = CodexImageService()
    service._isolate = True
    monkeypatch.setattr(module, "available_memory_kib", lambda: 100 * 1024)
    spawn = AsyncMock()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    with pytest.raises(MemoryError, match="worker未启动"):
        await service.generate_raw("测试插画")
    spawn.assert_not_called()


@pytest.mark.asyncio
async def test_disabled_fallback_never_constructs_paid_tts(monkeypatch):
    from moana.pipelines.picture_book import PictureBookPipeline

    pipeline = object.__new__(PictureBookPipeline)
    with pytest.raises(RuntimeError, match="付费回退已禁用"):
        await pipeline._retry_audio_with_fallback("短句", None, 0, 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("memory_error", [False, True])
async def test_memory_watcher_failure_stops_unit_and_reaps_cli(monkeypatch, memory_error):
    import moana.services.image.codex as module
    service = CodexImageService()
    service._isolate = True
    service._stop_unit = AsyncMock()
    monkeypatch.setattr(module, "MEMORY_POLL_SECONDS", 0.01)
    readings = []
    def memory():
        readings.append(True)
        if len(readings) == 1:
            return 512 * 1024
        if memory_error:
            raise OSError("内存采样失败")
        return 100 * 1024
    monkeypatch.setattr(module, "available_memory_kib", memory)
    original = asyncio.create_subprocess_exec
    processes = []
    async def spawn(*args, **kwargs):
        process = await original(sys.executable, "-c", "import time;time.sleep(30)", **kwargs)
        processes.append(process)
        return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    with pytest.raises(OSError if memory_error else MemoryError):
        await service.generate_raw("内存保护测试")
    service._stop_unit.assert_awaited_once()
    assert processes[0].returncode is not None


@pytest.mark.asyncio
async def test_failed_turn_cannot_import_leftover_bitmap(monkeypatch, tmp_path):
    service = CodexImageService()
    service._isolate = False
    service._home = tmp_path
    original = asyncio.create_subprocess_exec
    async def spawn(*args, **kwargs):
        thread_id = "00000000-0000-0000-0000-000000000002"
        directory = tmp_path / "generated_images" / thread_id
        directory.mkdir(parents=True)
        (directory / "partial.png").write_bytes(bitmap())
        return await original(sys.executable, "-c",
            "import sys,json;sys.stdin.read();print(json.dumps({'type':'thread.started','thread_id':sys.argv[1]}));print(json.dumps({'type':'turn.failed','error':{'message':'失败'}}))",
            thread_id, **kwargs)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    with pytest.raises(RuntimeError, match="未生成图片"):
        await service.generate_raw("不能导入失败轮次的图片")


def test_compressed_high_pixel_image_is_rejected_before_decode(monkeypatch):
    import moana.services.image.codex as module
    monkeypatch.setattr(module, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(ValueError, match="像素预算"):
        module._validate_bitmap(bitmap(), "PNG")


def test_mislabeled_bitmap_is_rejected():
    import moana.services.image.codex as module
    with pytest.raises(ValueError, match="实际格式"):
        module._validate_bitmap(bitmap(), "JPEG")


def test_event_reader_skips_oversized_and_non_object_events(tmp_path):
    import moana.services.image.codex as module
    log = tmp_path / "cli.log"
    with log.open("wb") as stream:
        stream.write(b'"' + b"x" * (1024 * 1024) + b'"\n')
        stream.write(b'[]\n{"type":"turn.completed"}\n')
    assert list(module._json_events(log)) == [{"type": "turn.completed"}]


async def test_systemd_stop_failure_attempts_kill_all(monkeypatch):
    commands = []
    async def spawn(*args, **kwargs):
        commands.append(args)
        return SimpleNamespace(returncode=1 if args[1] == "stop" else 0,
                               wait=AsyncMock())
    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    await CodexImageService._stop_unit("kids-test")
    assert commands == [("systemctl", "stop", "kids-test"),
                        ("systemctl", "kill", "--kill-who=all", "--signal=KILL", "kids-test")]
