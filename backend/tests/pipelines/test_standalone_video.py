"""Tests for standalone video pipeline."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from moana.pipelines.standalone_video import StandaloneVideoPipeline


class TestStandaloneVideoPipeline:
    """Test StandaloneVideoPipeline."""

    @pytest.fixture
    def mock_services(self):
        """Mock external services."""
        with patch("moana.pipelines.standalone_video.get_image_service") as img_mock, \
             patch("moana.pipelines.standalone_video.get_video_service") as vid_mock, \
             patch("moana.pipelines.standalone_video.SmartPromptAnalyzer") as analyzer_mock:

            # Mock image service
            img_service = MagicMock()
            img_service.generate = AsyncMock(return_value=MagicMock(
                url="https://example.com/image.png"
            ))
            img_mock.return_value = img_service

            # Mock video service
            vid_service = MagicMock()
            vid_service.generate = AsyncMock(return_value=MagicMock(
                video_url="https://example.com/video.mp4",
                duration=5,
                model="veo-3.1",
            ))
            vid_mock.return_value = vid_service

            # Mock analyzer
            analyzer = MagicMock()
            analyzer.analyze = AsyncMock(return_value=MagicMock(
                theme_category="cognition",
                theme_topic="花园探索",
                enhanced_prompt="小兔子在花园里开心玩耍",
                educational_goal="认识自然",
                title="小明的花园冒险",
            ))
            analyzer_mock.return_value = analyzer

            yield {
                "image": img_service,
                "video": vid_service,
                "analyzer": analyzer,
            }

    @pytest.mark.asyncio
    async def test_generate_with_auto_first_frame(self, mock_services):
        """Test video generation with auto-generated first frame."""
        pipeline = StandaloneVideoPipeline()

        result = await pipeline.generate(
            child_name="小明",
            age_months=36,
            custom_prompt="小兔子在花园里玩耍",
            generate_first_frame=True,
        )

        assert result["video_url"] == "https://example.com/video.mp4"
        assert result["first_frame_url"] == "https://example.com/image.png"
        assert result["title"] == "小明的花园冒险"
        assert mock_services["image"].generate.called
        assert mock_services["video"].generate.called

    @pytest.mark.asyncio
    async def test_generate_with_provided_first_frame(self, mock_services):
        """Test video generation with provided first frame URL."""
        pipeline = StandaloneVideoPipeline()

        result = await pipeline.generate(
            child_name="小明",
            age_months=36,
            custom_prompt="小兔子在花园里玩耍",
            first_frame_url="https://example.com/my-frame.png",
            generate_first_frame=False,
        )

        assert result["first_frame_url"] == "https://example.com/my-frame.png"
        assert not mock_services["image"].generate.called  # Should not generate
        assert mock_services["video"].generate.called
