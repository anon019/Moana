"""Tests for video generation services."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_video_service_interface():
    """Test video service has required interface."""
    from moana.services.video.base import BaseVideoService, VideoResult

    # Check abstract methods exist
    assert hasattr(BaseVideoService, "generate")
    assert hasattr(BaseVideoService, "provider_name")

    # Check VideoResult fields
    result = VideoResult(
        video_url="https://example.com/video.mp4",
        duration=30.0,
        thumbnail_url="https://example.com/thumb.jpg",
        model="wan2.5-i2v-preview",
    )
    assert result.video_url == "https://example.com/video.mp4"
    assert result.duration == 30.0
    assert result.has_audio is True


def test_wanx_service_initialization():
    """Test Wanx (阿里万相) service can be initialized."""
    from moana.services.video.wanx import WanxVideoService

    service = WanxVideoService()
    assert service is not None
    assert service.provider_name == "wanx"


@pytest.mark.asyncio
async def test_wanx_service_generate_from_image():
    """Test Wanx service generates video from image.

    通过 mock 服务内部方法来测试整体流程。
    """
    from moana.services.video.wanx import WanxVideoService
    from moana.services.video.base import VideoResult

    service = WanxVideoService()

    # Mock 内部方法
    service._convert_image_to_base64 = AsyncMock(
        return_value="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ=="
    )
    service._submit_task = AsyncMock(return_value="test-task-id")
    service._wait_for_task = AsyncMock(
        return_value="https://dashscope.oss.aliyuncs.com/video.mp4"
    )
    service._save_to_local_storage = AsyncMock(
        return_value="https://local.storage/video.mp4"
    )

    result = await service.generate(
        image_url="https://example.com/image.jpg",
        prompt="一个小女孩在花园里玩耍",
        duration_seconds=5,
    )

    # 验证结果
    assert result.video_url == "https://local.storage/video.mp4"
    assert result.duration == 5.0
    assert result.model == "wan2.6-i2v"
    assert result.has_audio is True

    # 验证调用链
    service._convert_image_to_base64.assert_called_once()
    service._submit_task.assert_called_once()
    service._wait_for_task.assert_called_once_with("test-task-id")
    service._save_to_local_storage.assert_called_once()


def test_get_video_service_wanx():
    """Test factory returns Wanx service."""
    import os
    os.environ["VIDEO_PROVIDER"] = "wanx"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.video import get_video_service
    from moana.services.video.wanx import WanxVideoService

    service = get_video_service()
    assert isinstance(service, WanxVideoService)


def test_get_video_service_invalid_provider():
    """Test factory raises error for unknown provider."""
    import os
    os.environ["VIDEO_PROVIDER"] = "unknown"

    from moana.config import get_settings
    get_settings.cache_clear()

    from moana.services.video import get_video_service

    with pytest.raises(ValueError, match="Unknown video provider"):
        get_video_service()
