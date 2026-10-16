from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice
from moana.services.tts.fish_speech import FishSpeechService


def get_tts_service() -> BaseTTSService:
    """Factory function to get TTS service based on config."""
    settings = get_settings()
    provider = settings.tts_provider.strip().lower()
    if provider == "disabled":
        raise ValueError("tts 生成已停用；gpt-6-luna 仅用于文本处理。")
    if provider in {"gemini", "vertex", "vertexai", "google"}:
        from moana.services.gemini_client import get_gemini_client
        get_gemini_client()

    if provider == "qwen":
        from moana.services.tts.qwen import QwenTTSService
        return QwenTTSService()
    elif provider == "minimax":
        from moana.services.tts.minimax import MiniMaxTTSService
        return MiniMaxTTSService()
    elif provider in {"fish_speech", "fish_audio", "fish_free_cli"}:
        return FishSpeechService()
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")


__all__ = ["BaseTTSService", "TTSResult", "Voice", "FishSpeechService", "get_tts_service"]
