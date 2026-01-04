import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


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
    from moana.services.llm.gemini import GeminiService

    with patch("moana.services.llm.gemini.genai") as mock_genai:
        service = GeminiService()
        assert service is not None
        assert service.model_name == "gemini-3-pro-preview"
        mock_genai.configure.assert_called_once()


def test_get_llm_service_gemini():
    """Test factory returns Gemini service when configured."""
    os.environ["LLM_PROVIDER"] = "gemini"

    from moana.config import get_settings
    get_settings.cache_clear()

    with patch("moana.services.llm.gemini.genai"):
        from moana.services.llm import get_llm_service
        from moana.services.llm.gemini import GeminiService

        service = get_llm_service()
        assert isinstance(service, GeminiService)


def test_get_llm_service_claude():
    """Test factory returns Claude service when configured."""
    os.environ["LLM_PROVIDER"] = "claude"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.llm import get_llm_service
    from moana.services.llm.claude import ClaudeService

    service = get_llm_service()
    assert isinstance(service, ClaudeService)
