import pytest


def test_tts_service_interface():
    """Test TTS service has required interface."""
    from moana.services.tts.base import BaseTTSService

    assert hasattr(BaseTTSService, "synthesize")
    assert hasattr(BaseTTSService, "list_voices")


def test_fish_speech_service_initialization():
    """Test Fish Speech service can be initialized."""
    from moana.services.tts.fish_speech import FishSpeechService

    service = FishSpeechService()
    assert service is not None
