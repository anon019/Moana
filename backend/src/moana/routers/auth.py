# src/moana/routers/auth.py
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from moana.database import get_db
from moana.models.user import User
from moana.schemas.auth import (
    WeChatLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from moana.services.wechat import WeChatService, WeChatError
from moana.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


async def get_or_create_user(
    db: AsyncSession,
    openid: str,
    unionid: Optional[str] = None,
    nickname: str = "",
    avatar_url: Optional[str] = None,
) -> User:
    """Get existing user or create new one."""
    from sqlalchemy import select

    # Try to find existing user
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if user:
        # Update user info if changed
        if nickname and user.nickname != nickname:
            user.nickname = nickname
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
        if unionid and not user.unionid:
            user.unionid = unionid
        await db.commit()
        return user

    # Create new user
    user = User(
        openid=openid,
        unionid=unionid,
        nickname=nickname,
        avatar_url=avatar_url,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current user from JWT token."""
    from sqlalchemy import select

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> User | None:
    """Get current user if authenticated, otherwise return None."""
    if not authorization:
        return None
    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

        # Create mock credentials to reuse get_current_user logic
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


@router.post("/wechat/login", response_model=TokenResponse)
async def wechat_login(
    request: WeChatLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Login with WeChat code."""
    wechat = WeChatService()

    try:
        session = await wechat.code_to_session(request.code)
    except WeChatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"WeChat login failed: {e.errmsg}",
        )

    openid = session["openid"]
    unionid = session.get("unionid")

    user = await get_or_create_user(db, openid=openid, unionid=unionid)

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Refresh access token."""
    from sqlalchemy import select

    payload = decode_access_token(request.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/mock-login", response_model=TokenResponse)
async def mock_login(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Mock login for admin panel (development/internal use)."""
    # Use a fixed admin user for the web admin panel
    ADMIN_OPENID = "admin_web_panel"

    user = await get_or_create_user(
        db,
        openid=ADMIN_OPENID,
        nickname="管理员",
    )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user info."""
    return UserResponse.model_validate(current_user)
