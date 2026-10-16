"""所有旧 Google 入口必须在建立连接前失败关闭。"""

import importlib
from unittest.mock import MagicMock

import pytest

from moana.config import Settings, get_settings
from moana.services.gemini_client import GoogleProviderDisabledError
from moana.services.llm.codex import CodexService


@pytest.mark.parametrize("provider", ["codex", "gemini", "vertex", "vertexai", "google"])
def test_legacy_google_text_config_uses_luna_cli(monkeypatch, provider):
    from moana.services.llm import get_llm_service

    monkeypatch.setenv("LLM_PROVIDER", provider)
    monkeypatch.setenv("CODEX_MODEL", "gpt-6-luna")
    get_settings.cache_clear()
    try:
        service = get_llm_service()
        assert isinstance(service, CodexService)
        assert service.model_name == "gpt-6-luna"
    finally:
        get_settings.cache_clear()


@pytest.mark.parametrize("kind,provider", [
    ("image", "gemini"), ("image", "imagen"), ("image", "vertexai"),
    ("tts", "gemini"), ("tts", "vertexai"),
    ("video", "veo"), ("video", "vertexai"),
])
def test_google_media_factories_fail_before_sdk_creation(monkeypatch, kind, provider):
    from google import genai

    constructor = MagicMock()
    monkeypatch.setattr(genai, "Client", constructor)
    monkeypatch.setenv(f"{kind.upper()}_PROVIDER", provider)
    module = importlib.import_module(f"moana.services.{kind}")
    get_settings.cache_clear()
    try:
        with pytest.raises(GoogleProviderDisabledError, match="已停用"):
            getattr(module, f"get_{kind}_service")()
        constructor.assert_not_called()
    finally:
        get_settings.cache_clear()


@pytest.mark.parametrize("module,service", [
    ("llm.gemini", "GeminiService"), ("image.gemini", "GeminiImageService"),
    ("image.google_imagen", "GoogleImagenService"), ("tts.gemini", "GeminiTTSService"),
    ("video.google_veo", "GoogleVeoService"),
])
def test_direct_google_services_used_by_scripts_are_disabled(module, service):
    cls = getattr(importlib.import_module(f"moana.services.{module}"), service)
    with pytest.raises(GoogleProviderDisabledError, match="已停用"):
        cls()


def test_google_media_is_disabled_by_default():
    settings = Settings(_env_file=None)
    assert settings.image_provider == "codex"
    assert settings.tts_provider == "fish_free_cli"
    assert settings.video_provider == "disabled"


@pytest.mark.parametrize("model", [
    "google/gemini-2.5-flash", "gemini-3-flash-preview", "vertex/test-model", "google/auto",
])
def test_openrouter_cannot_bypass_google_disable(monkeypatch, model):
    from moana.services.llm.openrouter import OpenRouterService

    monkeypatch.setenv("OPENROUTER_API_KEY", "offline-test")
    monkeypatch.setenv("OPENROUTER_MODEL", model)
    get_settings.cache_clear()
    try:
        with pytest.raises(GoogleProviderDisabledError, match="已停用"):
            OpenRouterService()
    finally:
        get_settings.cache_clear()
