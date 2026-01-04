"""Tests for Child API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_child_router_exists():
    """Test child router can be imported."""
    from moana.api.child import router
    assert router is not None


def test_get_child_settings_default():
    """Test getting child settings with defaults."""
    from moana.main import app

    client = TestClient(app)
    response = client.get("/api/v1/child/child_default/settings")

    assert response.status_code == 200
    data = response.json()
    assert data["child_id"] == "child_default"
    assert data["daily_limit_minutes"] == 60
    assert data["session_limit_minutes"] == 20
    assert data["rest_reminder_enabled"] is True


def test_update_child_settings():
    """Test updating child settings."""
    from moana.main import app

    client = TestClient(app)

    # 更新设置
    response = client.put(
        "/api/v1/child/child_update/settings",
        json={
            "daily_limit_minutes": 90,
            "session_limit_minutes": 30,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["daily_limit_minutes"] == 90
    assert data["session_limit_minutes"] == 30
    assert data["rest_reminder_enabled"] is True  # 未更新的保持默认


def test_update_child_settings_partial():
    """Test partially updating child settings."""
    from moana.main import app

    client = TestClient(app)

    # 只更新一个字段
    response = client.put(
        "/api/v1/child/child_partial/settings",
        json={"rest_reminder_enabled": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["daily_limit_minutes"] == 60  # 默认值
    assert data["rest_reminder_enabled"] is False


def test_get_updated_settings():
    """Test getting settings after update."""
    from moana.main import app

    client = TestClient(app)

    # 更新
    client.put(
        "/api/v1/child/child_get/settings",
        json={"daily_limit_minutes": 45},
    )

    # 获取
    response = client.get("/api/v1/child/child_get/settings")

    assert response.status_code == 200
    assert response.json()["daily_limit_minutes"] == 45
