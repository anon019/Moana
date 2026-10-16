from moana.config import get_settings
from moana.services.image.base import BaseImageService, ImageResult, ImageStyle
from moana.services.image.flux import FluxService
from moana.services.image.optimizer import ImageOptimizer


def get_image_service() -> BaseImageService:
    """Factory function to get image service based on config."""
    settings = get_settings()
    provider = settings.image_provider.strip().lower()
    if provider == "disabled":
        raise ValueError("image 生成已停用；gpt-6-luna 仅用于文本处理。")
    if provider in {"gemini", "vertex", "vertexai", "google", "imagen"}:
        from moana.services.gemini_client import get_gemini_client
        get_gemini_client()

    match provider:
        case "codex" | "gpt_image":
            from moana.services.image.codex import CodexImageService
            return CodexImageService()
        case "minimax":
            from moana.services.image.minimax import MiniMaxImageService
            return MiniMaxImageService()
        case "flux":
            return FluxService()
        case "qwen":
            from moana.services.image.qwen import QwenImageService
            return QwenImageService()
        case "wanx":
            from moana.services.image.wanx import WanxImageService
            return WanxImageService()
        case _:
            raise ValueError(f"Unknown image provider: {provider}")


__all__ = [
    "BaseImageService",
    "ImageResult",
    "ImageStyle",
    "FluxService",
    "ImageOptimizer",
    "get_image_service",
]
