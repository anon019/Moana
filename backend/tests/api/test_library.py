# tests/api/test_library.py
import pytest


def test_models_import():
    """Test library models can be imported."""
    from moana.models import Favorite, Share, SharePlatform
    assert Favorite is not None
    assert Share is not None
    assert SharePlatform is not None


def test_share_platform_enum():
    """Test SharePlatform enum values."""
    from moana.models import SharePlatform

    assert SharePlatform.WECHAT.value == "wechat"
    assert SharePlatform.WECHAT_MOMENTS.value == "wechat_moments"
    assert SharePlatform.QR_CODE.value == "qr_code"
    assert SharePlatform.LINK.value == "link"


def test_favorite_model():
    """Test Favorite model creation."""
    from moana.models import Favorite

    favorite = Favorite(
        user_id="user123",
        content_id="content456",
    )

    assert favorite.user_id == "user123"
    assert favorite.content_id == "content456"
    assert favorite.id is not None


def test_share_model():
    """Test Share model creation."""
    from moana.models import Share, SharePlatform

    share = Share(
        user_id="user123",
        content_id="content456",
        platform=SharePlatform.WECHAT,
    )

    assert share.user_id == "user123"
    assert share.content_id == "content456"
    assert share.platform == SharePlatform.WECHAT
    assert share.share_code is not None
    assert len(share.share_code) > 0
    assert share.view_count == 0


def test_share_service_import():
    """Test share services can be imported."""
    from moana.services.share import ShareService, PosterService
    assert ShareService is not None
    assert PosterService is not None


def test_share_result():
    """Test ShareResult dataclass."""
    from moana.services.share.share_service import ShareResult

    result = ShareResult(
        share_id="share123",
        share_code="abc123",
        share_url="https://example.com/share/abc123",
        poster_url="https://example.com/poster.png",
    )

    assert result.share_id == "share123"
    assert result.share_code == "abc123"

    result_dict = result.to_dict()
    assert "share_url" in result_dict


def test_poster_config():
    """Test PosterConfig dataclass."""
    from moana.services.share.poster import PosterConfig

    config = PosterConfig()
    assert config.width == 750
    assert config.height == 1334
    assert config.qr_size == 200


def test_library_router_import():
    """Test library router can be imported."""
    from moana.routers.library import router
    assert router is not None


@pytest.mark.asyncio
async def test_poster_service_not_installed():
    """Test PosterService graceful failure when PIL not available."""
    from moana.services.share import PosterService

    service = PosterService()
    # This may succeed or fail depending on Pillow availability
    result = await service.generate_simple_poster("Test Title")
    # Either way, should return a PosterResult
    assert result is not None
    assert hasattr(result, "success")


def test_check_favorite_model_logic():
    """Test check favorite logic with model."""
    from moana.models import Favorite

    favorite = Favorite(
        user_id="user-check-test",
        content_id="content-check-test",
    )

    assert favorite.id is not None
    assert favorite.user_id == "user-check-test"
    assert favorite.content_id == "content-check-test"
