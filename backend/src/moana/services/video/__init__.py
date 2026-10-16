# src/moana/services/video/__init__.py
from moana.config import get_settings

from moana.services.video.base import BaseVideoService, VideoResult


def get_video_service() -> BaseVideoService:
    """Factory function to get video service based on config."""
    settings = get_settings()
    provider = settings.video_provider.strip().lower()
    if provider == "disabled":
        raise ValueError("video 生成已停用；gpt-6-luna 仅用于文本处理。")
    if provider in {"veo", "gemini", "vertex", "vertexai", "google"}:
        from moana.services.gemini_client import get_gemini_client
        get_gemini_client()

    match provider:
        case "wanx":
            from moana.services.video.wanx import WanxVideoService
            return WanxVideoService()
        case "minimax":
            from moana.services.video.minimax import MiniMaxVideoService
            return MiniMaxVideoService()
        case _:
            raise ValueError(f"Unknown video provider: {provider}")


__all__ = ["get_video_service", "BaseVideoService", "VideoResult"]
