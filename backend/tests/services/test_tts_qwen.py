"""Tests for Qwen TTS service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os


def test_qwen_tts_service_initialization():
    """Test Qwen TTS service can be initialized."""
    from moana.services.tts.qwen import QwenTTSService

    service = QwenTTSService()
    assert service is not None


@pytest.mark.asyncio
async def test_qwen_tts_service_synthesize():
    """Test Qwen TTS service synthesize method using HTTP API."""
    from moana.services.tts.qwen import QwenTTSService

    # Mock HTTP response with URL (not base64)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "output": {
            "audio": {
                "url": "https://dashscope-result.oss.aliyuncs.com/audio.wav",
                "expires_at": 1765110852,
            },
            "finish_reason": "stop"
        },
        "usage": {"characters": 21},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("moana.services.tts.qwen.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client.return_value = mock_instance

        service = QwenTTSService()
        result = await service.synthesize(
            text="小莫，今天我们来学习数颜色",
            voice_id="Cherry",
        )

        # Result should be a URL
        assert result.audio_url == "https://dashscope-result.oss.aliyuncs.com/audio.wav"
        assert result.duration > 0  # Estimated from text length
        assert result.model == "qwen3-tts-flash"
        assert result.voice_id == "Cherry"


def test_get_tts_service_qwen():
    """Test factory returns Qwen service when configured."""
    os.environ["TTS_PROVIDER"] = "qwen"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.tts import get_tts_service
    from moana.services.tts.qwen import QwenTTSService

    service = get_tts_service()
    assert isinstance(service, QwenTTSService)


def test_get_tts_service_fish_speech():
    """Test factory returns Fish Speech service when configured."""
    os.environ["TTS_PROVIDER"] = "fish_speech"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.tts import get_tts_service
    from moana.services.tts.fish_speech import FishSpeechService

    service = get_tts_service()
    assert isinstance(service, FishSpeechService)
