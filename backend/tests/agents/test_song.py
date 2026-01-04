# tests/agents/test_song.py (新建)
import pytest
from unittest.mock import AsyncMock, patch


def test_song_agent_initialization():
    """Test Song Agent can be initialized."""
    from moana.agents.song import SongAgent

    agent = SongAgent()
    assert agent is not None


@pytest.mark.asyncio
async def test_song_agent_generate_lyrics():
    """Test Song Agent can generate lyrics."""
    from moana.agents.song import SongAgent
    from moana.agents.schemas import NurseryRhymeLyrics, LyricSection

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

    with patch("moana.agents.song.ClaudeService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_structured = AsyncMock(return_value=mock_lyrics)

        agent = SongAgent()
        result = await agent.generate_lyrics(
            child_name="小莫",
            age_months=22,
            theme_topic="刷牙",
            theme_category="habit",
        )

        assert result.title == "小莫刷牙歌"
        assert len(result.sections) == 2
        assert "刷牙" in result.theme_topic
