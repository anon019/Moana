"""Tests for MiniMax image generation service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os


def test_minimax_image_service_initialization():
    """Test MiniMax image service can be initialized."""
    from moana.services.image.minimax import MiniMaxImageService

    service = MiniMaxImageService()
    assert service is not None


@pytest.mark.asyncio
async def test_minimax_image_service_generate():
    """Test MiniMax image service generate method."""
    from moana.services.image.minimax import MiniMaxImageService
    from moana.services.image.base import ImageStyle

    # Mock MiniMax API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "base_resp": {"status_code": 0, "status_msg": "success"},
        "data": {
            "image_url": "https://minimax-cdn.com/generated-image.png",
        },
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        service = MiniMaxImageService()
        result = await service.generate(
            prompt="一个小女孩在花园里玩耍",
            style=ImageStyle.STORYBOOK,
            width=1024,
            height=1024,
        )

        assert result.url == "https://minimax-cdn.com/generated-image.png"
        assert result.model == "image-01"


def test_get_image_service_minimax():
    """Test factory returns MiniMax service when configured."""
    os.environ["IMAGE_PROVIDER"] = "minimax"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.image import get_image_service
    from moana.services.image.minimax import MiniMaxImageService

    service = get_image_service()
    assert isinstance(service, MiniMaxImageService)


def test_get_image_service_flux():
    """Test factory returns Flux service when configured."""
    os.environ["IMAGE_PROVIDER"] = "flux"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.image import get_image_service
    from moana.services.image.flux import FluxService

    service = get_image_service()
    assert isinstance(service, FluxService)
