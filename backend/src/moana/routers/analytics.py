# src/moana/routers/analytics.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from moana.config import get_settings
from moana.database import get_db
from moana.models import Child
from moana.models.user import User
from moana.routers.auth import get_current_user
from moana.services.analytics import AnalyticsStatsService
from moana.agents.analytics import AnalyticsAgent

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def _get_accessible_child(
    db: AsyncSession,
    child_id: str,
    current_user: User,
) -> Child | None:
    """获取用户可访问的宝贝（家庭共享模式）."""
    settings = get_settings()
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        return None

    if child.parent_id == current_user.id:
        return child

    admin_result = await db.execute(
        select(User.id).where(User.openid == settings.admin_openid)
    )
    admin_user_id = admin_result.scalar_one_or_none()

    if admin_user_id and child.parent_id == admin_user_id:
        return child

    return None


@router.get("/child/{child_id}/stats")
async def get_child_stats(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> dict:
    """Get statistics for a child (家庭共享模式).

    Args:
        child_id: Child ID
        days: Number of days to analyze (1-365)
    """
    child = await _get_accessible_child(db, child_id, current_user)

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    stats_service = AnalyticsStatsService()
    stats = await stats_service.get_child_stats(db, child_id, days)

    return stats.to_dict()


@router.get("/child/{child_id}/insights")
async def get_child_insights(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get AI-generated insights for a child (家庭共享模式).

    Args:
        child_id: Child ID
    """
    child = await _get_accessible_child(db, child_id, current_user)

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    stats_service = AnalyticsStatsService()
    stats = await stats_service.get_child_stats(db, child_id)

    analytics_agent = AnalyticsAgent()
    age_months = child.age_in_months()
    insights = await analytics_agent.generate_insights(
        stats=stats,
        child_name=child.name,
        age_months=age_months,
    )

    return {
        "stats": stats.to_dict(),
        "insights": insights.to_dict(),
    }


@router.get("/child/{child_id}/daily")
async def get_daily_breakdown(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: Annotated[int, Query(ge=1, le=30)] = 7,
) -> dict:
    """Get daily activity breakdown for a child (家庭共享模式).

    Args:
        child_id: Child ID
        days: Number of days (1-30)
    """
    child = await _get_accessible_child(db, child_id, current_user)

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    stats_service = AnalyticsStatsService()
    daily_stats = await stats_service.get_daily_breakdown(db, child_id, days)

    return {
        "child_id": child_id,
        "days": days,
        "daily_breakdown": [
            {
                "date": ds.date.isoformat() if hasattr(ds.date, 'isoformat') else str(ds.date),
                "total_plays": ds.total_plays,
                "total_duration": ds.total_duration,
            }
            for ds in daily_stats
        ],
    }
