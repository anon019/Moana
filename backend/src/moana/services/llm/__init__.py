from moana.config import get_settings
from moana.services.llm.base import BaseLLMService
from moana.services.llm.claude import ClaudeService
from moana.services.llm.codex import CodexService
from moana.services.llm.gemini import GeminiService
from moana.services.llm.openrouter import OpenRouterService


def get_llm_service() -> BaseLLMService:
    """根据配置返回 LLM 服务实例.

    Returns:
        BaseLLMService: 配置的 LLM 服务实例

    Raises:
        ValueError: 如果配置了不支持的 provider
    """
    settings = get_settings()
    provider = settings.llm_provider.strip().lower()

    if provider in {"codex", "gemini", "vertex", "vertexai", "google"}:
        return CodexService()
    elif provider == "claude":
        return ClaudeService()
    elif provider == "openrouter":
        return OpenRouterService()
    elif provider == "qwen":
        # Qwen LLM 服务待实现
        raise NotImplementedError("Qwen LLM service not implemented yet")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


__all__ = ["BaseLLMService", "CodexService", "ClaudeService", "GeminiService", "OpenRouterService", "get_llm_service"]
