import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_picture_book_pipeline_initialization():
    """Test pipeline can be initialized."""
    from moana.pipelines.picture_book import PictureBookPipeline

    pipeline = PictureBookPipeline()
    assert pipeline is not None


@pytest.mark.asyncio
async def test_picture_book_pipeline_generate():
    """Test pipeline can generate a complete picture book."""
    from moana.pipelines.picture_book import PictureBookPipeline
    from moana.agents.schemas import PictureBookOutline, PictureBookPage
    from moana.services.image.base import ImageResult
    from moana.services.tts.base import TTSResult

    mock_outline = PictureBookOutline(
        title="小莫学刷牙",
        theme_topic="刷牙",
        educational_goal="养成刷牙习惯",
        pages=[
            PictureBookPage(
                page_num=1,
                text="早上起床啦！",
                image_prompt="A girl waking up",
                interaction=None,
            )
        ],
        total_interactions=0,
    )

    mock_image = ImageResult(
        url="https://example.com/image.png",
        prompt="test",
        model="flux",
    )

    mock_tts = TTSResult(
        audio_url="https://example.com/audio.mp3",
        duration=3.0,
        voice_id="test",
        model="fish",
    )

    with patch("moana.pipelines.picture_book.StoryAgent") as MockAgent, \
         patch("moana.pipelines.picture_book.FluxService") as MockImage, \
         patch("moana.pipelines.picture_book.FishSpeechService") as MockTTS:

        MockAgent.return_value.generate_outline = AsyncMock(return_value=mock_outline)
        MockImage.return_value.generate = AsyncMock(return_value=mock_image)
        MockTTS.return_value.synthesize = AsyncMock(return_value=mock_tts)

        pipeline = PictureBookPipeline()
        result = await pipeline.generate(
            child_name="小莫",
            age_months=22,
            theme_topic="刷牙",
            theme_category="habit",
        )

        assert result["title"] == "小莫学刷牙"
        assert len(result["pages"]) == 1
        assert result["pages"][0]["image_url"] == "https://example.com/image.png"
