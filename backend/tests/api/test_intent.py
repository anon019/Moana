"""Tests for Intent API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch


def test_intent_router_exists():
    """Test intent router can be imported."""
    from moana.api.intent import router
    assert router is not None


@pytest.mark.asyncio
async def test_parse_intent_endpoint():
    """Test POST /api/v1/intent/parse endpoint."""
    from fastapi.testclient import TestClient
    from moana.main import app
    from moana.agents.schemas import ParsedIntent

    mock_intent = ParsedIntent(
        intent_type="life_event",
        original_input="明天要打疫苗",
        theme="打疫苗",
        category="habit",
        educational_goal="缓解恐惧",
        story_prompt="小动物打疫苗",
        song_prompt="勇敢歌",
        video_prompt=None,
        recommended_types=["picture_book"],
    )

    with patch("moana.api.intent.IntentAgent") as mock_agent_class:
        mock_agent = AsyncMock()
        mock_agent.parse.return_value = mock_intent
        mock_agent_class.return_value = mock_agent

        client = TestClient(app)
        response = client.post(
            "/api/v1/intent/parse",
            json={
                "child_name": "小莫",
                "age_months": 24,
                "user_input": "明天要打疫苗",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["intent_type"] == "life_event"
    assert data["theme"] == "打疫苗"
