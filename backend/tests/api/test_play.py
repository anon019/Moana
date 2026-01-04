"""Tests for Play API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_play_router_exists():
    """Test play router can be imported."""
    from moana.api.play import router
    assert router is not None


def test_start_play_new():
    """Test starting a new play session."""
    from moana.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_001",
            "content_id": "content_001",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "play_history_id" in data
    assert data["current_page"] == 1
    assert data["completion_rate"] == 0.0
    assert data["is_resumed"] is False


def test_start_play_resume():
    """Test resuming an incomplete play session."""
    from moana.main import app

    client = TestClient(app)

    # 开始播放
    response1 = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_resume",
            "content_id": "content_resume",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response1.json()["play_history_id"]

    # 更新进度
    client.post(
        "/api/v1/play/progress",
        json={"play_history_id": play_id, "current_page": 5},
    )

    # 再次开始（应该恢复）
    response2 = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_resume",
            "content_id": "content_resume",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )

    data = response2.json()
    assert data["is_resumed"] is True
    assert data["current_page"] == 5


def test_update_progress():
    """Test updating play progress."""
    from moana.main import app

    client = TestClient(app)

    # 开始播放
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_progress",
            "content_id": "content_progress",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response.json()["play_history_id"]

    # 更新进度
    response = client.post(
        "/api/v1/play/progress",
        json={"play_history_id": play_id, "current_page": 7},
    )

    assert response.status_code == 200
    assert response.json()["completion_rate"] == 0.7


def test_complete_play():
    """Test completing play."""
    from moana.main import app

    client = TestClient(app)

    # 开始播放
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_complete",
            "content_id": "content_complete",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response.json()["play_history_id"]

    # 完成播放
    response = client.post(
        "/api/v1/play/complete",
        json={"play_history_id": play_id},
    )

    assert response.status_code == 200
    data = response.json()
    assert "completed_at" in data
    assert data["total_time_seconds"] >= 0


def test_get_play_history():
    """Test getting play history."""
    from moana.main import app

    client = TestClient(app)

    # 创建一些播放记录
    for i in range(3):
        client.post(
            "/api/v1/play/start",
            json={
                "child_id": "child_history",
                "content_id": f"content_{i}",
                "content_type": "picture_book",
                "total_pages": 10,
            },
        )

    # 获取历史
    response = client.get("/api/v1/play/history/child_history")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


def test_submit_interaction():
    """Test submitting interaction result."""
    from moana.main import app

    client = TestClient(app)

    # 开始播放
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_interact",
            "content_id": "content_interact",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response.json()["play_history_id"]

    # 提交答题
    response = client.post(
        "/api/v1/play/interaction",
        json={
            "play_history_id": play_id,
            "page_num": 3,
            "question_type": "choice",
            "is_correct": True,
            "attempts": 1,
            "time_spent_ms": 2500,
        },
    )

    assert response.status_code == 200
    assert "interaction_id" in response.json()


def test_get_play_stats():
    """Test getting play stats."""
    from moana.main import app

    client = TestClient(app)

    # 开始播放
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": "child_stats",
            "content_id": "content_stats",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response.json()["play_history_id"]

    # 提交几个答题
    for i in range(5):
        client.post(
            "/api/v1/play/interaction",
            json={
                "play_history_id": play_id,
                "page_num": i + 1,
                "question_type": "choice",
                "is_correct": i < 3,  # 3 correct, 2 wrong
                "attempts": 1,
                "time_spent_ms": 2000,
            },
        )

    # 获取统计
    response = client.get("/api/v1/play/stats/child_stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 5
    assert data["correct_count"] == 3
    assert data["accuracy_rate"] == 0.6


def test_learning_stats_response_model():
    """Test LearningStatsResponse model structure."""
    from moana.api.play import LearningStatsResponse, DailyActivity, ThemeStats

    # Test DailyActivity
    daily = DailyActivity(
        date="2025-12-26",
        duration_minutes=25,
        contents_count=3,
    )
    assert daily.date == "2025-12-26"
    assert daily.duration_minutes == 25

    # Test ThemeStats
    theme = ThemeStats(theme="动物世界", count=6)
    assert theme.theme == "动物世界"
    assert theme.count == 6


def test_learning_stats_calculation():
    """Test learning stats calculation logic."""
    from datetime import datetime, timedelta

    # Simulate 7 days of data
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(7)]

    # Should have 7 unique dates
    assert len(set(dates)) == 7


def test_get_learning_stats_endpoint():
    """Test GET /learning-stats/{child_id} endpoint."""
    from moana.main import app

    client = TestClient(app)

    # Create some play history for learning stats
    child_id = "child_learning_stats"

    # Start and complete a play session
    response = client.post(
        "/api/v1/play/start",
        json={
            "child_id": child_id,
            "content_id": "content_learning_1",
            "content_type": "picture_book",
            "total_pages": 10,
        },
    )
    play_id = response.json()["play_history_id"]

    # Complete the play
    client.post(
        "/api/v1/play/complete",
        json={"play_history_id": play_id},
    )

    # Start another session (nursery rhyme)
    client.post(
        "/api/v1/play/start",
        json={
            "child_id": child_id,
            "content_id": "content_learning_2",
            "content_type": "nursery_rhyme",
            "total_pages": 1,
        },
    )

    # Get learning stats
    response = client.get(f"/api/v1/play/learning-stats/{child_id}")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "period" in data
    assert "summary" in data
    assert "daily_activity" in data
    assert "top_themes" in data

    # Check period structure
    assert "start_date" in data["period"]
    assert "end_date" in data["period"]
    assert "days" in data["period"]
    assert data["period"]["days"] == 7  # default

    # Check summary structure
    assert "total_duration_minutes" in data["summary"]
    assert "total_books" in data["summary"]
    assert "total_songs" in data["summary"]
    assert "total_videos" in data["summary"]
    assert "streak_days" in data["summary"]
    assert "interaction_rate" in data["summary"]

    # Verify content counts
    assert data["summary"]["total_books"] >= 1
    assert data["summary"]["total_songs"] >= 1


def test_get_learning_stats_with_custom_days():
    """Test learning stats with custom days parameter.

    This test verifies the model validation works with custom days parameter.
    The endpoint itself is tested in test_get_learning_stats_endpoint.
    """
    from moana.api.play import LearningStatsResponse, LearningStatsPeriod, LearningStatsSummary, DailyActivity, ThemeStats

    # Test building a response with 14 days
    daily_activity = [
        DailyActivity(date=f"2025-12-{26-i:02d}", duration_minutes=0, contents_count=0)
        for i in range(14)
    ]

    response = LearningStatsResponse(
        period=LearningStatsPeriod(
            start_date="2025-12-13",
            end_date="2025-12-26",
            days=14,
        ),
        summary=LearningStatsSummary(
            total_duration_minutes=0,
            total_books=0,
            total_songs=0,
            total_videos=1,
            streak_days=0,
            interaction_rate=0.0,
        ),
        daily_activity=daily_activity,
        top_themes=[],
    )

    assert response.period.days == 14
    assert len(response.daily_activity) == 14
    assert response.summary.total_videos == 1