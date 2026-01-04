# tests/api/test_auth.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_schemas_exist():
    """Test auth schemas can be imported."""
    from moana.schemas.auth import (
        WeChatLoginRequest,
        TokenResponse,
        RefreshTokenRequest,
        UserResponse,
    )
    assert WeChatLoginRequest is not None
    assert TokenResponse is not None
    assert RefreshTokenRequest is not None
    assert UserResponse is not None


def test_router_exists():
    """Test auth router can be imported."""
    from moana.routers.auth import router
    assert router is not None


def test_token_response_schema():
    """Test TokenResponse schema."""
    from moana.schemas.auth import TokenResponse

    token = TokenResponse(
        access_token="access123",
        refresh_token="refresh456",
    )
    assert token.access_token == "access123"
    assert token.refresh_token == "refresh456"
    assert token.token_type == "bearer"


def test_user_response_schema():
    """Test UserResponse schema."""
    from moana.schemas.auth import UserResponse

    user = UserResponse(
        id="user123",
        openid="wx_openid",
        nickname="测试用户",
        avatar_url="https://example.com/avatar.png",
    )
    assert user.id == "user123"
    assert user.nickname == "测试用户"


@pytest.mark.asyncio
async def test_get_or_create_user_new():
    """Test creating a new user."""
    from moana.routers.auth import get_or_create_user
    from moana.models.user import User

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    user = await get_or_create_user(
        db=mock_db,
        openid="wx_new_user",
        nickname="新用户",
    )

    assert isinstance(user, User)
    assert user.openid == "wx_new_user"
    assert user.nickname == "新用户"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_get_or_create_user_existing():
    """Test getting an existing user."""
    from moana.routers.auth import get_or_create_user
    from moana.models.user import User

    existing_user = User(openid="wx_existing", nickname="现有用户")

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db.execute.return_value = mock_result

    user = await get_or_create_user(
        db=mock_db,
        openid="wx_existing",
        nickname="现有用户",
    )

    assert user is existing_user
    mock_db.add.assert_not_called()
