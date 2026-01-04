from moana.config import get_settings
from moana.services.image.base import BaseImageService, ImageResult, ImageStyle
from moana.services.image.flux import FluxService
from moana.services.image.optimizer import ImageOptimizer


def get_image_service() -> BaseImageService:
    """Factory function to get image service based on config."""
    settings = get_settings()
    provider = settings.image_provider

    match provider:
        case "gemini":
            from moana.services.image.gemini import GeminiImageService
            return GeminiImageService()
        case "imagen":
            from moana.services.image.google_imagen import GoogleImagenService
            return GoogleImagenService()
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
    "ImagenQuotaExceededError",
    "ImagenSafetyFilterError",
]


# Import exceptions for convenience
def __getattr__(name):
    if name in ("ImagenQuotaExceededError", "ImagenSafetyFilterError"):
        from moana.services.image.google_imagen import (
            ImagenQuotaExceededError,
            ImagenSafetyFilterError,
        )
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
