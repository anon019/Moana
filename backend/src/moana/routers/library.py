# src/moana/routers/library.py
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from moana.database import get_db
from moana.models import Content, Favorite, Share, SharePlatform, User
from moana.routers.auth import get_current_user
from moana.services.share import ShareService, PosterService

router = APIRouter(prefix="/library", tags=["library"])


class FavoriteRequest(BaseModel):
    """Request to add/remove favorite."""
    content_id: str


class ShareRequest(BaseModel):
    """Request to create share."""
    content_id: str
    platform: SharePlatform
    generate_poster: bool = False


class ContentResponse(BaseModel):
    """Response for content item."""
    id: str
    title: str
    content_type: str
    theme_category: str
    theme_topic: str
    is_favorited: bool = False

    model_config = {"from_attributes": True}


@router.get("/favorites")
async def get_favorites(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Get user's favorite content."""
    # Get favorites with content
    query = (
        select(Content, Favorite)
        .join(Favorite, Favorite.content_id == Content.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    rows = result.all()

    # Get total count
    count_query = select(func.count(Favorite.id)).where(
        Favorite.user_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    contents = []
    for content, favorite in rows:
        contents.append({
            "id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "theme_category": content.theme_category,
            "theme_topic": content.theme_topic,
            "is_favorited": True,
            "favorited_at": favorite.created_at.isoformat(),
        })

    return {
        "items": contents,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/favorites")
async def add_favorite(
    request: FavoriteRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Add content to favorites."""
    # Check if content exists
    result = await db.execute(
        select(Content).where(Content.id == request.content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )

    # Check if already favorited
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.content_id == request.content_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {"message": "Already favorited", "favorite_id": existing.id}

    # Create favorite
    favorite = Favorite(
        user_id=current_user.id,
        content_id=request.content_id,
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return {"message": "Added to favorites", "favorite_id": favorite.id}


class CheckFavoriteResponse(BaseModel):
    """Response for favorite check."""
    is_favorited: bool
    favorite_id: Optional[str] = None


@router.get("/favorites/check/{content_id}")
async def check_favorite(
    content_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> CheckFavoriteResponse:
    """Check if content is favorited by current user."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.content_id == content_id,
        )
    )
    favorite = result.scalar_one_or_none()

    return CheckFavoriteResponse(
        is_favorited=favorite is not None,
        favorite_id=favorite.id if favorite else None,
    )


@router.delete("/favorites/{content_id}")
async def remove_favorite(
    content_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Remove content from favorites."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.content_id == content_id,
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    await db.delete(favorite)
    await db.commit()

    return {"message": "Removed from favorites"}


@router.post("/share")
async def create_share(
    request: ShareRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Create a share for content."""
    # Check if content exists
    result = await db.execute(
        select(Content).where(Content.id == request.content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )

    poster_url = None
    if request.generate_poster:
        poster_service = PosterService()
        poster_result = await poster_service.generate_poster(
            title=content.title,
            subtitle=content.theme_topic,
            qr_data=f"https://moana.example.com/c/{content.id}",
        )
        # In production, would upload to storage and get URL
        if poster_result.success:
            poster_url = f"https://moana.example.com/posters/{content.id}.png"

    share_service = ShareService()
    share_result = await share_service.create_share(
        db=db,
        user_id=current_user.id,
        content_id=request.content_id,
        platform=request.platform,
        poster_url=poster_url,
    )

    return share_result.to_dict()


@router.get("/share/{share_code}")
async def get_share(
    share_code: str,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Get share by code (public endpoint)."""
    share_service = ShareService()
    share = await share_service.get_share_by_code(db, share_code)

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found",
        )

    # Increment view count
    await share_service.increment_view_count(db, share_code)

    # Get content
    result = await db.execute(
        select(Content).where(Content.id == share.content_id)
    )
    content = result.scalar_one_or_none()

    return {
        "share_code": share.share_code,
        "content": {
            "id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "theme_topic": content.theme_topic,
        } if content else None,
        "poster_url": share.poster_url,
        "view_count": share.view_count + 1,
    }


@router.get("/my-shares")
async def get_my_shares(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> dict:
    """Get user's shares."""
    share_service = ShareService()
    shares = await share_service.get_user_shares(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": s.id,
                "share_code": s.share_code,
                "content_id": s.content_id,
                "platform": s.platform.value,
                "view_count": s.view_count,
                "poster_url": s.poster_url,
                "created_at": s.created_at.isoformat(),
            }
            for s in shares
        ],
        "limit": limit,
        "offset": offset,
    }
