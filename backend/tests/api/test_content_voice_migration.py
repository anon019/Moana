"""音色选项和修复入口只使用 Fish；历史模型来源不得被当前配置覆盖。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from moana.api import content as api
from moana.models.content import ContentType
from moana.services.tts.base import Voice


@pytest.mark.parametrize('has_preview', [False, True])
async def test_voice_options_use_current_fish_voice_and_existing_preview(monkeypatch, tmp_path, has_preview):
    import moana.services.tts as tts
    voice_id = 'a' * 32
    settings = SimpleNamespace(storage_local_path=str(tmp_path),
                               storage_base_url='https://example.invalid/media',
                               fish_speech_voice_id=voice_id)
    service = SimpleNamespace(list_voices=AsyncMock(return_value=[Voice(voice_id, 'Fish 中文旁白', 'zh')]),
                              close=AsyncMock())
    monkeypatch.setattr(api, 'get_settings', lambda: settings)
    monkeypatch.setattr(tts, 'get_tts_service', lambda: service)
    relative = f'voice-preview/fish_speech/{voice_id}.mp3'
    if has_preview:
        target = tmp_path / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(b'preview')
    response = await api.get_tts_voices()
    assert response['default_provider'] == 'fish_speech'
    assert response['default_voice'] == voice_id
    voice = response['providers'][0]['voices'][0]
    assert voice['id'] == voice_id and voice['gender'] == 'neutral'
    assert voice['preview_url'] == (settings.storage_base_url + '/' + relative if has_preview else None)
    service.close.assert_awaited_once()
    options = await api.get_style_options()
    assert options['tts_voices'] == response['providers'][0]['voices']


@pytest.mark.parametrize('metadata', [
    {'image_model': 'unknown', 'tts_model': 'unknown'},
    {'image_model': 'gemini-historical-image', 'tts_model': 'gemini-historical-tts'},
    {'image_model': 'not_exposed_by_tool', 'requested_image_model': 'gpt-image-2.5-sunburst',
     'image_tool': 'codex_cli', 'tts_model': 's2.1-pro-free'},
])
async def test_asset_details_keep_stored_model_and_voice_provenance(metadata):
    content = SimpleNamespace(content_type=ContentType.PICTURE_BOOK, generated_by=metadata,
                              content_data={'pages': []}, personalization={'voice_id': 'Kore'},
                              theme_category='cognition', theme_topic='test',
                              id='historical-id', title='历史绘本')
    db = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: content)))
    result = await api.get_asset_details('historical-id', db)
    config = result['generation_config']
    assert config['image']['model'] == metadata['image_model']
    assert config['audio']['model'] == metadata['tts_model']
    assert config['audio']['voice_id'] == 'Kore'
    assert config['image']['requested_model'] == metadata.get('requested_image_model')


async def test_audio_repair_calls_only_current_fish_service_once(monkeypatch):
    import moana.services.image as images
    import moana.services.tts as tts
    service = SimpleNamespace(validate_configuration=Mock(),
                              synthesize=AsyncMock(side_effect=ValueError('Fish 配置不完整')))
    monkeypatch.setattr(tts, 'get_tts_service', Mock(return_value=service))
    monkeypatch.setattr(images, 'get_image_service', Mock(side_effect=AssertionError('音频修复不应初始化图片服务')))
    monkeypatch.setattr(api, '_task_status', {})
    db = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(fetchone=lambda: [
        {'pages': [{'text': '测试旁白'}]},
    ])))
    class Session:
        async def __aenter__(self):
            return db
        async def __aexit__(self, *args):
            return False
    monkeypatch.setattr(api, 'async_session_factory', Session)
    await api._do_auto_repair('task', 'content', [{'page_num': 1, 'audio_failed': True}], 'Kore', 3, 1)
    service.validate_configuration.assert_called_once_with('Kore')
    service.synthesize.assert_awaited_once_with(text='测试旁白', voice_id='Kore')
    assert api._task_status['task']['stage'] == 'repair_failed'
    tts.get_tts_service.assert_called_once_with()


async def test_repaired_asset_metadata_overrides_only_its_page():
    content = SimpleNamespace(
        content_type=ContentType.PICTURE_BOOK,
        generated_by={"tts_model": "gemini-old", "image_model": "gemini-image"},
        content_data={"pages": [
            {"page_num": 1, "audio_url": "old.mp3"},
            {"page_num": 2, "audio_url": "new.mp3", "audio_model": "s2.1-pro-free",
             "audio_voice_id": "a" * 32, "image_url": "new.webp",
             "image_model": "not_exposed_by_tool", "image_tool": "codex_cli"},
        ]}, personalization={"voice_id": "Kore"}, theme_category="cognition",
        theme_topic="test", id="mixed", title="混合来源",
    )
    db = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: content)))
    result = await api.get_asset_details("mixed", db)
    old_audio, new_image, new_audio = result["assets"]
    assert old_audio["model"] == "gemini-old" and old_audio["voice_id"] == "Kore"
    assert new_audio["model"] == "s2.1-pro-free" and new_audio["voice_id"] == "a" * 32
    assert new_image["model"] == "not_exposed_by_tool"
    assert result["generation_config"]["audio"]["model"] == "gemini-old"


async def test_successful_audio_repair_persists_actual_voice_and_model(monkeypatch):
    import json
    import moana.services.tts as tts
    from moana.services.tts.base import TTSResult
    service = SimpleNamespace(validate_configuration=Mock(), synthesize=AsyncMock(
        return_value=TTSResult("new.mp3", 2.5, "b" * 32, "s2.1-pro-free")))
    monkeypatch.setattr(tts, "get_tts_service", lambda: service)
    monkeypatch.setattr(api, "_task_status", {})
    original = {"pages": [{"text": "旁白", "audio_url": ""}],
                "failed_pages": [{"page_num": 1, "audio_failed": True}]}
    db = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(fetchone=lambda: [original])),
                         commit=AsyncMock())
    class Session:
        async def __aenter__(self):
            return db
        async def __aexit__(self, *args):
            return False
    monkeypatch.setattr(api, "async_session_factory", Session)
    await api._do_auto_repair("task", "content", [{"page_num": 1, "audio_failed": True}], "Kore", 3, 0)
    saved = [json.loads(call.args[1]["data"]) for call in db.execute.call_args_list
             if len(call.args) > 1 and "data" in call.args[1]][0]
    assert saved["pages"][0]["audio_model"] == "s2.1-pro-free"
    assert saved["pages"][0]["audio_voice_id"] == "b" * 32
    assert saved["failed_pages"] is None
    assert api._task_status["task"]["status"] == "completed"
