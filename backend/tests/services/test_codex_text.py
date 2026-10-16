"""文本迁移的离线回归：路由、结构校验与超时回收。"""

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, ValidationError

from moana.config import get_settings
from moana.services.llm.codex import CodexService, parse_json_response
from moana.services.llm.codex_client import CodexClient


@pytest.fixture
def codex_settings(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "codex")
    monkeypatch.setenv("CODEX_MODEL", "gpt-6-luna")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_text_factory_uses_luna(codex_settings):
    from moana.services.llm import get_llm_service
    service = get_llm_service()
    assert isinstance(service, CodexService)
    assert service.model_name == "gpt-6-luna"
    settings = get_settings()
    assert settings.gemini_image_model == "gemini-3.1-flash-image"
    assert settings.gemini_tts_model == "gemini-3.1-flash-tts-preview"


@pytest.mark.parametrize("text", ['{"name":', '[]', 'null', ''])
def test_rejects_incomplete_or_non_object_json(text):
    with pytest.raises(ValueError):
        parse_json_response(text)


async def test_structured_output_validates_schema(codex_settings):
    class Answer(BaseModel):
        count: int

    service = CodexService()
    service._client.create = AsyncMock(return_value=SimpleNamespace(choices=[
        SimpleNamespace(message=SimpleNamespace(content='```json\n{"count":3}\n```')),
    ]))
    result = await service.generate_structured("分析给定材料", Answer)
    assert result.count == 3
    assert service._client.create.call_args.kwargs["model"] == "gpt-6-luna"
    service._client.create.return_value.choices[0].message.content = '{"count":"bad"}'
    with pytest.raises(ValidationError):
        await service.generate_structured("分析给定材料", Answer)


async def test_cli_returns_only_completed_result(monkeypatch):
    recorded = {}

    async def spawn(*args, **kwargs):
        recorded.update(args=args, env=kwargs["env"])
        Path(args[args.index("--output-last-message") + 1]).write_text('{"ok":true}')
        return SimpleNamespace(returncode=0, communicate=AsyncMock(
            return_value=(b'{"type":"turn.completed"}\n', b'')))

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setenv("GOOGLE_API_KEY", "must-not-be-forwarded")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-forwarded")
    monkeypatch.setenv("CODEX_API_KEY", "must-not-be-forwarded")
    # 显式有效期限优先于失效的环境配置。
    monkeypatch.setenv("CODEX_TIMEOUT", "NaN")
    result = await CodexClient().create(
        model="gpt-6-luna", messages=[{"role": "user", "content": "分析"}], timeout=1,
    )
    assert result.choices[0].message.content == '{"ok":true}'
    assert "GOOGLE_API_KEY" not in recorded["env"]
    assert "OPENAI_API_KEY" not in recorded["env"]
    assert "CODEX_API_KEY" not in recorded["env"]
    assert '--ignore-user-config' in recorded['args']
    assert 'features.shell_tool=false' in recorded['args']
    assert 'features.image_generation=false' in recorded['args']
    assert 'forced_login_method="chatgpt"' in recorded['args']


@pytest.mark.parametrize('timeout', [0, -1, float('nan'), float('inf'), -float('inf'),
                                    '', 'bad', False, True])
async def test_cli_rejects_invalid_timeout_before_spawn(monkeypatch, timeout):
    spawn = AsyncMock()
    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    monkeypatch.setenv('CODEX_TIMEOUT', '600')
    with pytest.raises(ValueError, match='有限正数'):
        await CodexClient().create(model='gpt-6-luna', messages=[], timeout=timeout)
    spawn.assert_not_awaited()


@pytest.mark.parametrize('timeout', ['0', '-1', 'NaN', 'Infinity', '', 'bad'])
async def test_cli_rejects_invalid_environment_timeout(monkeypatch, timeout):
    spawn = AsyncMock()
    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    monkeypatch.setenv('CODEX_TIMEOUT', timeout)
    with pytest.raises(ValueError, match='有限正数'):
        await CodexClient().create(model='gpt-6-luna', messages=[])
    spawn.assert_not_awaited()


async def test_cli_rejects_unencodable_prompt_before_spawn(monkeypatch):
    spawn = AsyncMock()
    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    with pytest.raises(UnicodeEncodeError):
        await CodexClient().create(
            model='gpt-6-luna', messages=[{'role': 'user', 'content': '\ud800'}],
        )
    spawn.assert_not_awaited()


@pytest.mark.parametrize('events,answer,returncode', [
    ([{'type': 'turn.failed'}], 'partial', 0),
    ([{'type': 'turn.completed'}, {'type': 'error'}], 'partial', 0),
    ([{'type': 'thread.started'}], 'partial', 0),
    ([{'type': 'turn.completed'}], '', 0),
    ([{'type': 'turn.completed'}], 'partial', 1),
    ([None, []], 'partial', 0),
])
async def test_cli_rejects_failed_or_incomplete_result(monkeypatch, events, answer, returncode):
    directories = []

    async def spawn(*args, **kwargs):
        output = Path(args[args.index('--output-last-message') + 1])
        directories.append(output.parent)
        output.write_text(answer)
        stdout = '\n'.join(json.dumps(event) for event in events).encode()
        return SimpleNamespace(returncode=returncode, communicate=AsyncMock(
            return_value=(stdout, b'')))

    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    with pytest.raises(RuntimeError, match='Codex'):
        await CodexClient().create(model='gpt-6-luna', messages=[])
    assert directories and not directories[0].exists()


@pytest.mark.parametrize('returncode', [None, 0])
async def test_cli_timeout_reaps_process(monkeypatch, returncode):
    process = SimpleNamespace(returncode=returncode, pid=123456)
    calls = []
    directories = []

    async def communicate(*args):
        if args:
            await asyncio.sleep(10)
        return b'', b''

    process.communicate = AsyncMock(side_effect=communicate)
    async def spawn(*args, **kwargs):
        directories.append(Path(args[args.index('--output-last-message') + 1]).parent)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr("moana.services.llm.codex_client.os.killpg", lambda *args: calls.append(args))
    with pytest.raises(TimeoutError):
        await CodexClient().create(
            model="gpt-6-luna", messages=[{"role": "user", "content": "分析"}], timeout=0.01,
        )
    assert calls[0][0] == process.pid
    assert process.communicate.await_count == 2
    assert not directories[0].exists()


async def test_cli_cancellation_reaps_process(monkeypatch):
    started = asyncio.Event()
    process = SimpleNamespace(returncode=None, pid=123456)
    directories = []
    calls = []

    async def communicate(*args):
        if args:
            started.set()
            await asyncio.Future()
        return b'', b''

    process.communicate = AsyncMock(side_effect=communicate)

    async def spawn(*args, **kwargs):
        directories.append(Path(args[args.index('--output-last-message') + 1]).parent)
        return process

    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    monkeypatch.setattr('moana.services.llm.codex_client.os.killpg', lambda *args: calls.append(args))
    task = asyncio.create_task(CodexClient().create(
        model='gpt-6-luna', messages=[{'role': 'user', 'content': '分析'}],
    ))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls[0][0] == process.pid
    assert process.communicate.await_count == 2
    assert not directories[0].exists()


async def test_prompt_analyzer_uses_async_text_service(monkeypatch):
    from moana.services.smart.prompt_analyzer import SmartPromptAnalyzer
    client = SimpleNamespace(generate=AsyncMock(return_value='{"theme_category":"nature"}'))
    monkeypatch.setattr("moana.services.smart.prompt_analyzer.get_llm_service", lambda: client)
    result = await SmartPromptAnalyzer().analyze("看树叶", "小朋友", 30, "picture_book")
    assert result.theme_category == "nature"
    client.generate.assert_awaited_once()
