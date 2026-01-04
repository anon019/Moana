"""Tests for Plan API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch


def test_plan_router_exists():
    """Test plan router can be imported."""
    from moana.api.plan import router
    assert router is not None


@pytest.mark.asyncio
async def test_generate_weekly_plan_endpoint():
    """Test POST /api/v1/plan/weekly endpoint."""
    from fastapi.testclient import TestClient
    from moana.main import app
    from moana.agents.schemas import DayPlan, WeeklyPlan

    mock_plan = WeeklyPlan(
        week_start="2025-12-09",
        child_id="child_001",
        child_name="小莫",
        age_months=24,
        days=[
            DayPlan(
                day=1,
                date="2025-12-09",
                theme="刷牙",
                category="habit",
                content_types=["picture_book"],
                story_hint="test",
                song_hint=None,
            )
        ],
    )

    with patch("moana.api.plan.PlannerAgent") as mock_agent_class:
        mock_agent = AsyncMock()
        mock_agent.generate_weekly_plan.return_value = mock_plan
        mock_agent_class.return_value = mock_agent

        client = TestClient(app)
        response = client.post(
            "/api/v1/plan/weekly",
            json={
                "child_id": "child_001",
                "child_name": "小莫",
                "age_months": 24,
                "preferences": [],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["child_name"] == "小莫"
    assert len(data["days"]) >= 1
