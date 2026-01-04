# src/moana/api/child.py
"""Child API - 孩子管理相关端点."""
from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from moana.database import get_db
from moana.models.child import Child
from moana.models.user import User
from moana.routers.auth import get_current_user

router = APIRouter()


# ========== Request/Response Schemas ==========

class ChildResponse(BaseModel):
    """孩子信息响应."""
    id: str
    name: str
    birth_date: date
    avatar_url: Optional[str] = None
    favorite_characters: list[str] = []
    interests: list[str] = []
    current_stage: Optional[str] = None

    model_config = {"from_attributes": True}


class CreateChildRequest(BaseModel):
    """创建孩子请求."""
    name: str = Field(..., min_length=1, max_length=50, description="孩子名字")
    birth_date: date = Field(..., description="出生日期")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    favorite_characters: list[str] = Field(default_factory=list, description="喜欢的角色")
    interests: list[str] = Field(default_factory=list, description="兴趣爱好")


class UpdateChildRequest(BaseModel):
    """更新孩子请求."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="孩子名字")
    birth_date: Optional[date] = Field(None, description="出生日期")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    favorite_characters: Optional[list[str]] = Field(None, description="喜欢的角色")
    interests: Optional[list[str]] = Field(None, description="兴趣爱好")
    current_stage: Optional[str] = Field(None, max_length=50, description="当前阶段")


class ChildSettingsResponse(BaseModel):
    """孩子设置响应."""
    child_id: str
    daily_limit_minutes: int
    session_limit_minutes: int
    rest_reminder_enabled: bool


class UpdateChildSettingsRequest(BaseModel):
    """更新孩子设置请求."""
    daily_limit_minutes: Optional[int] = Field(
        default=None,
        ge=10,
        le=180,
        description="Daily limit in minutes (10-180)"
    )
    session_limit_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=60,
        description="Session limit in minutes (5-60)"
    )
    rest_reminder_enabled: Optional[bool] = Field(
        default=None,
        description="Whether to enable rest reminder"
    )


# ========== 内存存储（MVP 阶段，后续替换为数据库） ==========

_child_settings: dict[str, dict] = {}

# 默认设置
_default_settings = {
    "daily_limit_minutes": 60,
    "session_limit_minutes": 20,
    "rest_reminder_enabled": True,
}


def _get_or_create_settings(child_id: str) -> dict:
    """获取或创建孩子设置."""
    if child_id not in _child_settings:
        _child_settings[child_id] = {
            "child_id": child_id,
            **_default_settings,
        }
    return _child_settings[child_id]


# ========== 家庭共享模式配置 ==========
# 管理员 openid，用于家庭共享模式
ADMIN_OPENID = "admin_web_panel"


async def get_accessible_child(
    db: AsyncSession,
    child_id: str,
    current_user: User,
) -> Child | None:
    """获取用户可访问的宝贝（家庭共享模式）.

    用户可以访问：
    1. 自己创建的宝贝
    2. 管理员创建的宝贝（家庭共享）
    """
    # 先查找这个宝贝
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        return None

    # 检查是否是自己的宝贝
    if child.parent_id == current_user.id:
        return child

    # 检查是否是管理员的宝贝（家庭共享）
    admin_result = await db.execute(
        select(User).where(User.openid == ADMIN_OPENID)
    )
    admin_user = admin_result.scalar_one_or_none()

    if admin_user and child.parent_id == admin_user.id:
        return child

    return None


# ========== API Endpoints ==========

@router.get("/list", response_model=list[ChildResponse])
async def list_children(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ChildResponse]:
    """获取孩子列表（家庭共享模式）.

    家庭共享模式：所有家庭成员共享管理员创建的宝贝档案。
    - 如果当前用户有自己的宝贝，返回自己的
    - 否则返回管理员创建的宝贝（共享给所有家庭成员）
    """
    # 先查找当前用户自己的宝贝
    result = await db.execute(
        select(Child).where(Child.parent_id == current_user.id)
    )
    children = result.scalars().all()

    # 如果用户有自己的宝贝，直接返回
    if children:
        return [ChildResponse.model_validate(child) for child in children]

    # 家庭共享模式：返回管理员的宝贝
    admin_result = await db.execute(
        select(User).where(User.openid == ADMIN_OPENID)
    )
    admin_user = admin_result.scalar_one_or_none()

    if admin_user:
        result = await db.execute(
            select(Child).where(Child.parent_id == admin_user.id)
        )
        children = result.scalars().all()
        return [ChildResponse.model_validate(child) for child in children]

    return []


@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    request: CreateChildRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChildResponse:
    """创建新的孩子档案.

    需要认证，创建的孩子会关联到当前用户。
    """
    child = Child(
        name=request.name,
        birth_date=request.birth_date,
        avatar_url=request.avatar_url,
        favorite_characters=request.favorite_characters,
        interests=request.interests,
        parent_id=current_user.id,
    )
    db.add(child)
    await db.commit()
    await db.refresh(child)
    return ChildResponse.model_validate(child)


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChildResponse:
    """获取孩子详情（家庭共享模式）.

    可以获取自己的宝贝或管理员创建的共享宝贝。
    """
    child = await get_accessible_child(db, child_id, current_user)

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    return ChildResponse.model_validate(child)


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: str,
    request: UpdateChildRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChildResponse:
    """更新孩子信息.

    需要认证，只能更新自己创建的孩子信息。
    只更新请求中提供的非 None 字段。
    """
    result = await db.execute(
        select(Child).where(
            Child.id == child_id,
            Child.parent_id == current_user.id,
        )
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    # 更新非 None 字段
    if request.name is not None:
        child.name = request.name
    if request.birth_date is not None:
        child.birth_date = request.birth_date
    if request.avatar_url is not None:
        child.avatar_url = request.avatar_url
    if request.favorite_characters is not None:
        child.favorite_characters = request.favorite_characters
    if request.interests is not None:
        child.interests = request.interests
    if request.current_stage is not None:
        child.current_stage = request.current_stage

    await db.commit()
    await db.refresh(child)
    return ChildResponse.model_validate(child)


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """删除孩子档案.

    需要认证，只能删除自己创建的孩子。
    """
    result = await db.execute(
        select(Child).where(
            Child.id == child_id,
            Child.parent_id == current_user.id,
        )
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    await db.delete(child)
    await db.commit()


@router.get("/{child_id}/settings", response_model=ChildSettingsResponse)
async def get_child_settings(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChildSettingsResponse:
    """获取孩子设置（家庭共享模式）.

    如果没有设置过，返回默认值。
    可以获取自己的宝贝或管理员创建的共享宝贝的设置。
    """
    child = await get_accessible_child(db, child_id, current_user)

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    settings = _get_or_create_settings(child_id)
    return ChildSettingsResponse(**settings)


@router.put("/{child_id}/settings", response_model=ChildSettingsResponse)
async def update_child_settings(
    child_id: str,
    request: UpdateChildSettingsRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChildSettingsResponse:
    """更新孩子设置.

    只更新请求中提供的字段。
    需要认证，只能更新自己孩子的设置。
    """
    # 验证孩子存在且属于当前用户
    result = await db.execute(
        select(Child).where(
            Child.id == child_id,
            Child.parent_id == current_user.id,
        )
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    settings = _get_or_create_settings(child_id)

    # 更新非 None 字段
    if request.daily_limit_minutes is not None:
        settings["daily_limit_minutes"] = request.daily_limit_minutes
    if request.session_limit_minutes is not None:
        settings["session_limit_minutes"] = request.session_limit_minutes
    if request.rest_reminder_enabled is not None:
        settings["rest_reminder_enabled"] = request.rest_reminder_enabled

    return ChildSettingsResponse(**settings)
