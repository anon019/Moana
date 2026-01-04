# tests/models/test_user.py
import pytest
from datetime import datetime


def test_user_model_exists():
    """Test User model can be imported."""
    from moana.models.user import User
    assert User is not None


def test_user_model_fields():
    """Test User model has required fields."""
    from moana.models.user import User

    user = User(
        openid="wx_openid_123",
        nickname="测试用户",
        avatar_url="https://example.com/avatar.png",
    )

    assert user.openid == "wx_openid_123"
    assert user.nickname == "测试用户"
    assert user.avatar_url == "https://example.com/avatar.png"
    assert user.id is not None
    assert user.unionid is None
    assert user.phone is None


def test_user_default_values():
    """Test User model default values."""
    from moana.models.user import User

    user = User(openid="wx_123")
    assert user.nickname == ""
    assert user.avatar_url is None
