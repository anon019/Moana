import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_music_service_interface():
    """Test music service has required interface."""
    from moana.services.music.base import BaseMusicService, MusicResult, MusicStyle

    # Check abstract methods exist
    assert hasattr(BaseMusicService, "generate")

    # Check MusicResult fields
    result = MusicResult(
        audio_url="https://example.com/song.mp3",
        duration=42.5,
        lyrics="test lyrics",
        model="music-2.0",
    )
    assert result.audio_url == "https://example.com/song.mp3"
    assert result.duration == 42.5


def test_music_style_enum():
    """Test MusicStyle enumeration."""
    from moana.services.music.base import MusicStyle

    assert MusicStyle.CHEERFUL == "cheerful"
    assert MusicStyle.GENTLE == "gentle"
    assert MusicStyle.PLAYFUL == "playful"


def test_minimax_service_initialization():
    """Test MiniMax service can be initialized."""
    from moana.services.music.minimax import MiniMaxMusicService

    service = MiniMaxMusicService()
    assert service is not None
    assert service.provider_name == "minimax"


@pytest.mark.asyncio
async def test_minimax_service_generate():
    """Test MiniMax service generate method."""
    from moana.services.music.minimax import MiniMaxMusicService
    from moana.services.music.base import MusicStyle

    # Mock MiniMax API response format
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "audio": "https://example.com/generated.mp3",
            "status": 2,
        },
        "extra_info": {
            "music_duration": 42500,  # Duration in milliseconds
            "music_sample_rate": 44100,
        },
        "base_resp": {
            "status_code": 0,
            "status_msg": "success",
        },
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        service = MiniMaxMusicService()
        result = await service.generate(
            lyrics="[Verse]\n小莫早起床",
            style_prompt="cheerful children song",
            duration_seconds=45,
            style=MusicStyle.CHEERFUL,
        )

        assert result.audio_url == "https://example.com/generated.mp3"
        assert result.duration == 42.5  # 42500ms -> 42.5s
        assert result.model == "music-2.0"


import os


def test_get_music_service_minimax():
    """Test factory returns MiniMax service."""
    os.environ["MUSIC_PROVIDER"] = "minimax"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.music import get_music_service
    from moana.services.music.minimax import MiniMaxMusicService

    service = get_music_service()
    assert isinstance(service, MiniMaxMusicService)


def test_get_music_service_invalid_provider():
    """Test factory raises error for unknown provider."""
    os.environ["MUSIC_PROVIDER"] = "unknown"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.music import get_music_service

    with pytest.raises(ValueError, match="Unknown music provider"):
        get_music_service()
