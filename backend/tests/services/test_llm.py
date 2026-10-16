import os
import pytest
from unittest.mock import patch


def test_llm_service_interface():
    """Test LLM service has required interface."""
    from moana.services.llm.base import BaseLLMService

    # Check abstract methods exist
    assert hasattr(BaseLLMService, "generate")
    assert hasattr(BaseLLMService, "generate_structured")


@pytest.mark.asyncio
async def test_claude_service_initialization():
    """Test Claude service can be initialized."""
    from moana.services.llm.claude import ClaudeService

    service = ClaudeService()
    assert service is not None
    assert service.model_name is not None


def test_gemini_service_initialization():
    """Test Gemini service can be initialized."""
    from moana.config import get_settings
    from moana.services.llm.gemini import GeminiService

    with patch("moana.services.llm.gemini.get_gemini_client") as mock_get_client:
        service = GeminiService()
        assert service is not None
        assert service.model_name == get_settings().google_model
        mock_get_client.assert_called_once_with()


def test_get_llm_service_gemini():
    """旧 Gemini 文本配置也只使用 Codex CLI。"""
    os.environ["LLM_PROVIDER"] = "gemini"

    from moana.config import get_settings
    get_settings.cache_clear()

    with patch("moana.services.llm.gemini.get_gemini_client"):
        from moana.services.llm import get_llm_service
        from moana.services.llm.codex import CodexService

        service = get_llm_service()
        assert isinstance(service, CodexService)


def test_get_llm_service_claude():
    """Test factory returns Claude service when configured."""
    os.environ["LLM_PROVIDER"] = "claude"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.llm import get_llm_service
    from moana.services.llm.claude import ClaudeService

    service = get_llm_service()
    assert isinstance(service, ClaudeService)
