# src/moana/services/wechat.py
from typing import Optional
import httpx

from moana.config import get_settings


class WeChatError(Exception):
    """WeChat API error."""

    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"WeChat error {errcode}: {errmsg}")


class WeChatService:
    """Service for WeChat OAuth operations."""

    OAUTH_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"
    MINIPROGRAM_URL = "https://api.weixin.qq.com/sns/jscode2session"

    def __init__(self):
        settings = get_settings()
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret

    async def code_to_session(self, code: str) -> dict:
        """Exchange auth code for session info (Mini Program).

        Args:
            code: The auth code from WeChat Mini Program

        Returns:
            Dict with openid, session_key, and optionally unionid

        Raises:
            WeChatError: If WeChat API returns an error
        """
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.MINIPROGRAM_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WeChatError(data["errcode"], data.get("errmsg", "Unknown error"))

        return data

    async def code_to_token(self, code: str) -> dict:
        """Exchange auth code for access token (Web/H5).

        Args:
            code: The auth code from WeChat OAuth

        Returns:
            Dict with access_token, openid, and optionally unionid

        Raises:
            WeChatError: If WeChat API returns an error
        """
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.OAUTH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if "errcode" in data:
            raise WeChatError(data["errcode"], data.get("errmsg", "Unknown error"))

        return data

    async def get_user_info(
        self,
        access_token: str,
        openid: str,
    ) -> dict:
        """Get user info from WeChat.

        Args:
            access_token: WeChat access token
            openid: User's openid

        Returns:
            Dict with user profile info
        """
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.USERINFO_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if "errcode" in data:
            raise WeChatError(data["errcode"], data.get("errmsg", "Unknown error"))

        return data
