# tests/services/test_analytics.py
import pytest


def test_analytics_imports():
    """Test analytics service can be imported."""
    from moana.services.analytics import AnalyticsStatsService, ChildStats
    assert AnalyticsStatsService is not None
    assert ChildStats is not None


def test_child_stats():
    """Test ChildStats dataclass."""
    from moana.services.analytics import ChildStats
    from moana.models import ContentType

    stats = ChildStats(
        child_id="child123",
        total_plays=50,
        total_duration=1800,
        favorite_content_type=ContentType.PICTURE_BOOK,
        streak_days=5,
    )

    assert stats.child_id == "child123"
    assert stats.total_plays == 50
    assert stats.total_duration == 1800
    assert stats.streak_days == 5

    stats_dict = stats.to_dict()
    assert stats_dict["total_plays"] == 50
    assert stats_dict["favorite_content_type"] == "picture_book"


def test_analytics_agent_import():
    """Test AnalyticsAgent can be imported."""
    from moana.agents import AnalyticsAgent
    assert AnalyticsAgent is not None


def test_analytics_insight():
    """Test AnalyticsInsight dataclass."""
    from moana.agents.analytics import AnalyticsInsight

    insight = AnalyticsInsight(
        summary="学习表现良好",
        recommendations=["多看绘本", "尝试新内容"],
        highlights=["连续5天学习"],
        concerns=[],
    )

    assert insight.summary == "学习表现良好"
    assert len(insight.recommendations) == 2

    insight_dict = insight.to_dict()
    assert "summary" in insight_dict
    assert "recommendations" in insight_dict


def test_analytics_router_import():
    """Test analytics router can be imported."""
    from moana.routers.analytics import router
    assert router is not None


@pytest.mark.asyncio
async def test_analytics_agent_default_insight():
    """Test AnalyticsAgent generates default insight."""
    from moana.agents.analytics import AnalyticsAgent
    from moana.services.analytics import ChildStats

    agent = AnalyticsAgent()
    stats = ChildStats(
        child_id="child123",
        total_plays=10,
        total_duration=600,
        streak_days=3,
    )

    insight = agent._generate_default_insight(stats, "小明")

    assert "小明" in insight.summary
    assert len(insight.highlights) > 0
    assert len(insight.recommendations) > 0
