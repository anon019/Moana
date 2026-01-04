from moana.config import get_settings
from moana.services.music.base import BaseMusicService, MusicResult, MusicStyle


def get_music_service() -> BaseMusicService:
    """Factory function to get music service based on configuration."""
    settings = get_settings()
    provider = settings.music_provider

    match provider:
        case "suno":
            from moana.services.music.suno import SunoMusicService
            return SunoMusicService()
        case "minimax":
            from moana.services.music.minimax import MiniMaxMusicService
            return MiniMaxMusicService()
        case _:
            raise ValueError(f"Unknown music provider: {provider}")


__all__ = [
    "BaseMusicService",
    "MusicResult",
    "MusicStyle",
    "get_music_service",
]
