"""Tests for video generation pipeline."""
from unittest.mock import AsyncMock

import pytest


def test_video_pipeline_initialization():
    """Test VideoPipeline can be initialized."""
    from moana.pipelines.video import VideoPipeline

    pipeline = VideoPipeline()
    assert pipeline is not None


@pytest.mark.asyncio
async def test_video_pipeline_generate_from_picture_book():
    """Test pipeline generates video from picture book data.

    优化后的 Pipeline 只调用一次视频服务 API，使用第一张和最后一张图片。
    """
    import base64
    from moana.pipelines.video import VideoPipeline
    from moana.services.video.base import VideoResult

    # Create fake video data for mock
    fake_video = b'\x00\x00\x00\x1c\x66\x74\x79\x70' + b'\x00' * 100
    fake_video_url = f"data:video/mp4;base64,{base64.b64encode(fake_video).decode()}"

    # Mock video service
    mock_video_service = AsyncMock()
    mock_video_service.generate.return_value = VideoResult(
        video_url=fake_video_url,
        duration=8.0,
        thumbnail_url="https://example.com/thumb.jpg",
        model="veo-3.1",
        has_audio=True,
    )

    pipeline = VideoPipeline(video_service=mock_video_service)

    # Simulated picture book data (from PictureBookPipeline output)
    picture_book_data = {
        "title": "小莫的花园冒险",
        "pages": [
            {
                "page_num": 1,
                "text": "小莫走进了美丽的花园。",
                "image_url": "https://example.com/page1.jpg",
            },
            {
                "page_num": 2,
                "text": "她看到了五颜六色的花朵。",
                "image_url": "https://example.com/page2.jpg",
            },
        ],
    }

    result = await pipeline.generate(picture_book_data=picture_book_data)

    # 优化后只调用一次 generate（使用第一张图片作为首帧，最后一张作为尾帧）
    assert mock_video_service.generate.call_count == 1

    # 验证调用参数
    call_args = mock_video_service.generate.call_args
    assert call_args.kwargs["image_url"] == "https://example.com/page1.jpg"
    assert call_args.kwargs["last_frame_url"] == "https://example.com/page2.jpg"
    assert "小莫的花园冒险" in call_args.kwargs["prompt"]

    assert result["title"] == "小莫的花园冒险"
    assert result["video_url"] == fake_video_url
    assert result["duration"] == 8.0
    assert result["thumbnail_url"] == "https://example.com/page1.jpg"
    assert len(result["clips"]) == 1


@pytest.mark.asyncio
async def test_video_pipeline_with_progress_callback():
    """Test pipeline reports progress during generation."""
    from moana.pipelines.video import VideoPipeline, GenerationProgress
    from moana.services.video.base import VideoResult

    mock_video_service = AsyncMock()
    mock_video_service.generate.return_value = VideoResult(
        video_url="https://example.com/scene.mp4",
        duration=8.0,
        thumbnail_url="https://example.com/thumb.jpg",
        model="veo-3.1",
    )

    pipeline = VideoPipeline(video_service=mock_video_service)

    progress_updates = []

    def on_progress(progress: GenerationProgress):
        progress_updates.append(progress)

    picture_book_data = {
        "title": "测试绘本",
        "pages": [
            {"page_num": 1, "text": "第一页", "image_url": "https://example.com/1.jpg"},
        ],
    }

    await pipeline.generate(
        picture_book_data=picture_book_data,
        on_progress=on_progress,
    )

    # Should have received progress updates with "video_generation" stage
    assert len(progress_updates) == 2  # 开始 + 完成
    assert all(p.stage == "video_generation" for p in progress_updates)
    assert progress_updates[0].message == "正在生成视频..."
    assert progress_updates[1].message == "视频生成完成"


@pytest.mark.asyncio
async def test_video_pipeline_single_page():
    """Test pipeline handles single-page picture book correctly."""
    from moana.pipelines.video import VideoPipeline
    from moana.services.video.base import VideoResult

    mock_video_service = AsyncMock()
    mock_video_service.generate.return_value = VideoResult(
        video_url="https://example.com/video.mp4",
        duration=8.0,
        thumbnail_url="https://example.com/thumb.jpg",
        model="veo-3.1",
    )

    pipeline = VideoPipeline(video_service=mock_video_service)

    # 单页绘本
    picture_book_data = {
        "title": "单页故事",
        "pages": [
            {"page_num": 1, "text": "唯一的一页", "image_url": "https://example.com/only.jpg"},
        ],
    }

    result = await pipeline.generate(picture_book_data=picture_book_data)

    # 只有一页时，last_frame_url 应该为 None
    call_args = mock_video_service.generate.call_args
    assert call_args.kwargs["image_url"] == "https://example.com/only.jpg"
    assert call_args.kwargs["last_frame_url"] is None

    assert result["title"] == "单页故事"
    assert result["video_url"] == "https://example.com/video.mp4"


@pytest.mark.asyncio
async def test_video_pipeline_empty_pages_raises_error():
    """Test pipeline raises error when picture book has no pages."""
    from moana.pipelines.video import VideoPipeline

    pipeline = VideoPipeline()

    picture_book_data = {
        "title": "空绘本",
        "pages": [],
    }

    with pytest.raises(ValueError, match="绘本数据中没有页面"):
        await pipeline.generate(picture_book_data=picture_book_data)
