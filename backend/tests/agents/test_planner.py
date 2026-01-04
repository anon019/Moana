"""Tests for Planner Agent."""
import pytest
from unittest.mock import AsyncMock, patch


def test_planner_agent_initialization():
    """Test PlannerAgent can be initialized."""
    from moana.agents.planner import PlannerAgent

    agent = PlannerAgent()
    assert agent is not None


@pytest.mark.asyncio
async def test_planner_agent_generate_weekly_plan():
    """Test generating weekly plan."""
    from moana.agents.planner import PlannerAgent
    from moana.agents.schemas import WeeklyPlan

    # Mock LLM response
    mock_plan = {
        "days": [
            {
                "day": i,
                "date": f"2025-12-{8+i:02d}",
                "theme": "刷牙" if i % 2 == 1 else "颜色",
                "category": "habit" if i % 2 == 1 else "cognition",
                "content_types": ["picture_book", "nursery_rhyme"],
                "story_hint": f"Day {i} story hint",
                "song_hint": f"Day {i} song hint",
            }
            for i in range(1, 8)
        ]
    }

    with patch("moana.agents.planner.get_llm_service") as mock_llm:
        mock_service = AsyncMock()
        mock_service.generate_structured.return_value = mock_plan
        mock_llm.return_value = mock_service

        agent = PlannerAgent()
        result = await agent.generate_weekly_plan(
            child_id="child_001",
            child_name="小莫",
            age_months=24,
            preferences=["恐龙"],
            learned_themes=["洗手"],
        )

    assert isinstance(result, WeeklyPlan)
    assert result.child_name == "小莫"
    assert len(result.days) == 7


@pytest.mark.asyncio
async def test_planner_avoids_learned_themes():
    """Test that planner avoids recently learned themes."""
    from moana.agents.planner import PlannerAgent

    agent = PlannerAgent()
    prompt = agent._build_prompt(
        child_name="小莫",
        age_months=24,
        preferences=[],
        learned_themes=["刷牙", "洗手"],
        available_themes=["刷牙", "洗手", "颜色", "形状"],
    )

    assert "刷牙" in prompt
    assert "洗手" in prompt
    assert "避开" in prompt or "不要重复" in prompt
