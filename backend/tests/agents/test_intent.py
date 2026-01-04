"""Tests for Intent Agent."""
import pytest
from unittest.mock import AsyncMock, patch


def test_intent_agent_initialization():
    """Test IntentAgent can be initialized."""
    from moana.agents.intent import IntentAgent

    agent = IntentAgent()
    assert agent is not None


@pytest.mark.asyncio
async def test_intent_agent_parse_life_event():
    """Test parsing life event input."""
    from moana.agents.intent import IntentAgent
    from moana.agents.schemas import ParsedIntent

    mock_result = {
        "intent_type": "life_event",
        "theme": "打疫苗",
        "category": "habit",
        "educational_goal": "缓解打疫苗恐惧",
        "story_prompt": "小动物打疫苗的故事",
        "song_prompt": "勇敢歌",
        "video_prompt": None,
        "recommended_types": ["picture_book", "nursery_rhyme"],
    }

    with patch("moana.agents.intent.get_llm_service") as mock_llm:
        mock_service = AsyncMock()
        mock_service.generate_structured.return_value = mock_result
        mock_llm.return_value = mock_service

        agent = IntentAgent()
        result = await agent.parse(
            child_name="小莫",
            age_months=24,
            user_input="明天要打疫苗，孩子有点害怕",
        )

    assert isinstance(result, ParsedIntent)
    assert result.intent_type == "life_event"
    assert result.theme == "打疫苗"


@pytest.mark.asyncio
async def test_intent_agent_parse_interest():
    """Test parsing interest input."""
    from moana.agents.intent import IntentAgent
    from moana.agents.schemas import ParsedIntent

    mock_result = {
        "intent_type": "interest",
        "theme": "恐龙",
        "category": "cognition",
        "educational_goal": "认识恐龙，激发探索兴趣",
        "story_prompt": "小朋友穿越到恐龙世界的冒险",
        "song_prompt": "恐龙歌，各种恐龙的名字",
        "video_prompt": "恐龙世界动画",
        "recommended_types": ["picture_book", "nursery_rhyme", "video"],
    }

    with patch("moana.agents.intent.get_llm_service") as mock_llm:
        mock_service = AsyncMock()
        mock_service.generate_structured.return_value = mock_result
        mock_llm.return_value = mock_service

        agent = IntentAgent()
        result = await agent.parse(
            child_name="小莫",
            age_months=30,
            user_input="孩子最近超喜欢恐龙",
        )

    assert result.intent_type == "interest"
    assert result.theme == "恐龙"
    assert "video" in result.recommended_types
