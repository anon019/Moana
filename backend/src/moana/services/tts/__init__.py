from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice
from moana.services.tts.fish_speech import FishSpeechService


def get_tts_service() -> BaseTTSService:
    """Factory function to get TTS service based on config."""
    settings = get_settings()
    provider = settings.tts_provider

    if provider == "gemini":
        from moana.services.tts.gemini import GeminiTTSService
        return GeminiTTSService()
    elif provider == "qwen":
        from moana.services.tts.qwen import QwenTTSService
        return QwenTTSService()
    elif provider == "minimax":
        from moana.services.tts.minimax import MiniMaxTTSService
        return MiniMaxTTSService()
    elif provider == "fish_speech":
        return FishSpeechService()
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")


__all__ = ["BaseTTSService", "TTSResult", "Voice", "FishSpeechService", "get_tts_service"]
