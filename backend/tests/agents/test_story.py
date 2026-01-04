import pytest
from unittest.mock import AsyncMock, patch


def test_story_agent_initialization():
    """Test Story Agent can be initialized."""
    from moana.agents.story import StoryAgent

    agent = StoryAgent()
    assert agent is not None


@pytest.mark.asyncio
async def test_story_agent_generate_outline():
    """Test Story Agent can generate a story outline."""
    from moana.agents.story import StoryAgent
    from moana.agents.schemas import PictureBookOutline

    # Mock the LLM service
    mock_outline = PictureBookOutline(
        title="小莫学刷牙",
        theme_topic="刷牙",
        educational_goal="养成早晚刷牙的好习惯",
        pages=[
            {
                "page_num": 1,
                "text": "早上起床啦！小莫揉揉眼睛。",
                "image_prompt": "A cute 2-year-old Chinese girl waking up in bed",
                "interaction": None,
            }
        ],
        total_interactions=2,
    )

    with patch("moana.agents.story.ClaudeService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_structured = AsyncMock(return_value=mock_outline)

        agent = StoryAgent()
        outline = await agent.generate_outline(
            child_name="小莫",
            age_months=22,
            theme_topic="刷牙",
            theme_category="habit",
        )

        assert outline.title == "小莫学刷牙"
        assert len(outline.pages) >= 1
