# src/moana/schemas/auth.py
from typing import Optional
from pydantic import BaseModel


class WeChatLoginRequest(BaseModel):
    """Request schema for WeChat login."""
    code: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class UserResponse(BaseModel):
    """Response schema for user info."""
    id: str
    openid: str
    nickname: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}
