# tests/services/test_wechat.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def create_mock_response(data: dict):
    """Create a mock httpx Response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


@pytest.mark.asyncio
async def test_wechat_service_exists():
    """Test WeChat service can be imported."""
    from moana.services.wechat import WeChatService
    assert WeChatService is not None


@pytest.mark.asyncio
async def test_code_to_session_success():
    """Test successful code to session exchange."""
    from moana.services.wechat import WeChatService

    mock_response = {
        "openid": "wx_openid_123",
        "session_key": "session_key_abc",
        "unionid": "wx_unionid_456",
    }

    with patch("moana.services.wechat.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = create_mock_response(mock_response)

        service = WeChatService()
        result = await service.code_to_session("auth_code_123")

        assert result["openid"] == "wx_openid_123"
        assert result["session_key"] == "session_key_abc"


@pytest.mark.asyncio
async def test_code_to_session_error():
    """Test error handling in code to session."""
    from moana.services.wechat import WeChatService, WeChatError

    mock_response = {
        "errcode": 40029,
        "errmsg": "invalid code",
    }

    with patch("moana.services.wechat.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = create_mock_response(mock_response)

        service = WeChatService()

        with pytest.raises(WeChatError) as exc_info:
            await service.code_to_session("invalid_code")

        assert "invalid code" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_info():
    """Test get user info from WeChat."""
    from moana.services.wechat import WeChatService

    mock_response = {
        "openid": "wx_openid_123",
        "nickname": "测试用户",
        "headimgurl": "https://example.com/avatar.png",
    }

    with patch("moana.services.wechat.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = create_mock_response(mock_response)

        service = WeChatService()
        result = await service.get_user_info("access_token", "openid")

        assert result["nickname"] == "测试用户"
