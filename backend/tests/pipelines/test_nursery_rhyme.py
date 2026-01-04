# tests/pipelines/test_nursery_rhyme.py (新建)
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_nursery_rhyme_pipeline_initialization():
    """Test pipeline can be initialized."""
    from moana.pipelines.nursery_rhyme import NurseryRhymePipeline

    pipeline = NurseryRhymePipeline()
    assert pipeline is not None


@pytest.mark.asyncio
async def test_nursery_rhyme_pipeline_generate():
    """Test pipeline can generate a complete nursery rhyme."""
    from moana.pipelines.nursery_rhyme import NurseryRhymePipeline
    from moana.agents.schemas import NurseryRhymeLyrics, LyricSection
    from moana.services.music.base import MusicResult
    from moana.services.image.base import ImageResult

    mock_lyrics = NurseryRhymeLyrics(
        title="小莫刷牙歌",
        theme_topic="刷牙",
        lyrics_text="[Verse]\n小莫早起床\n[Chorus]\n刷刷刷",
        sections=[
            LyricSection(tag="verse", content="小莫早起床", order=1),
            LyricSection(tag="chorus", content="刷刷刷", order=2),
        ],
        style_prompt="cheerful children song",
        cover_prompt="A cute girl brushing teeth",
        educational_goal="养成刷牙习惯",
    )

    mock_music = MusicResult(
        audio_url="https://example.com/song.mp3",
        duration=42.5,
        lyrics="test",
        model="music-2.0",
    )

    mock_image = ImageResult(
        url="https://example.com/cover.png",
        prompt="test",
        model="flux",
    )

    with patch("moana.pipelines.nursery_rhyme.SongAgent") as MockAgent, \
         patch("moana.pipelines.nursery_rhyme.get_music_service") as MockMusicFactory, \
         patch("moana.pipelines.nursery_rhyme.FluxService") as MockImage:

        MockAgent.return_value.generate_lyrics = AsyncMock(return_value=mock_lyrics)
        MockMusicFactory.return_value.generate = AsyncMock(return_value=mock_music)
        MockImage.return_value.generate = AsyncMock(return_value=mock_image)

        pipeline = NurseryRhymePipeline()
        result = await pipeline.generate(
            child_name="小莫",
            age_months=22,
            theme_topic="刷牙",
            theme_category="habit",
        )

        assert result["title"] == "小莫刷牙歌"
        assert result["audio_url"] == "https://example.com/song.mp3"
        assert result["cover_url"] == "https://example.com/cover.png"
        assert result["audio_duration"] == 42.5
        assert len(result["lyrics"]["sections"]) == 2
