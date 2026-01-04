# src/moana/services/analytics/stats.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from moana.models import PlayHistory, Content, ContentType


@dataclass
class ContentStats:
    """Statistics for a specific content type."""
    content_type: ContentType
    total_plays: int = 0
    total_duration: int = 0  # seconds
    unique_contents: int = 0


@dataclass
class DailyStats:
    """Daily statistics."""
    date: datetime
    total_plays: int = 0
    total_duration: int = 0
    content_breakdown: dict = field(default_factory=dict)


@dataclass
class ChildStats:
    """Complete statistics for a child."""
    child_id: str
    total_plays: int = 0
    total_duration: int = 0  # seconds
    favorite_content_type: Optional[ContentType] = None
    content_stats: list[ContentStats] = field(default_factory=list)
    daily_stats: list[DailyStats] = field(default_factory=list)
    streak_days: int = 0
    last_activity: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "child_id": self.child_id,
            "total_plays": self.total_plays,
            "total_duration": self.total_duration,
            "favorite_content_type": self.favorite_content_type.value if self.favorite_content_type else None,
            "content_stats": [
                {
                    "content_type": cs.content_type.value,
                    "total_plays": cs.total_plays,
                    "total_duration": cs.total_duration,
                    "unique_contents": cs.unique_contents,
                }
                for cs in self.content_stats
            ],
            "streak_days": self.streak_days,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }


class AnalyticsStatsService:
    """Service for computing analytics statistics."""

    async def get_child_stats(
        self,
        db: AsyncSession,
        child_id: str,
        days: int = 30,
    ) -> ChildStats:
        """Get comprehensive statistics for a child.

        Args:
            db: Database session
            child_id: Child ID
            days: Number of days to analyze

        Returns:
            ChildStats with aggregated statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get total plays and duration
        total_query = select(
            func.count(PlayHistory.id).label("total_plays"),
            func.sum(PlayHistory.duration).label("total_duration"),
        ).where(
            PlayHistory.child_id == child_id,
            PlayHistory.created_at >= start_date,
        )

        result = await db.execute(total_query)
        row = result.first()
        total_plays = row.total_plays or 0
        total_duration = row.total_duration or 0

        # Get stats by content type
        content_type_query = select(
            Content.content_type,
            func.count(PlayHistory.id).label("plays"),
            func.sum(PlayHistory.duration).label("duration"),
            func.count(func.distinct(PlayHistory.content_id)).label("unique_contents"),
        ).join(
            Content, PlayHistory.content_id == Content.id
        ).where(
            PlayHistory.child_id == child_id,
            PlayHistory.created_at >= start_date,
        ).group_by(Content.content_type)

        result = await db.execute(content_type_query)
        content_stats = []
        max_plays = 0
        favorite_type = None

        for row in result:
            stats = ContentStats(
                content_type=row.content_type,
                total_plays=row.plays or 0,
                total_duration=row.duration or 0,
                unique_contents=row.unique_contents or 0,
            )
            content_stats.append(stats)

            if stats.total_plays > max_plays:
                max_plays = stats.total_plays
                favorite_type = stats.content_type

        # Get last activity
        last_activity_query = select(
            func.max(PlayHistory.created_at)
        ).where(PlayHistory.child_id == child_id)

        result = await db.execute(last_activity_query)
        last_activity = result.scalar()

        # Calculate streak (simplified)
        streak = await self._calculate_streak(db, child_id)

        return ChildStats(
            child_id=child_id,
            total_plays=total_plays,
            total_duration=total_duration,
            favorite_content_type=favorite_type,
            content_stats=content_stats,
            streak_days=streak,
            last_activity=last_activity,
        )

    async def _calculate_streak(
        self,
        db: AsyncSession,
        child_id: str,
    ) -> int:
        """Calculate consecutive days streak.

        Args:
            db: Database session
            child_id: Child ID

        Returns:
            Number of consecutive days with activity
        """
        # Get distinct activity dates in last 30 days
        query = select(
            func.date(PlayHistory.created_at).label("activity_date")
        ).where(
            PlayHistory.child_id == child_id,
            PlayHistory.created_at >= datetime.utcnow() - timedelta(days=30),
        ).group_by(
            func.date(PlayHistory.created_at)
        ).order_by(
            func.date(PlayHistory.created_at).desc()
        )

        result = await db.execute(query)
        dates = [row.activity_date for row in result]

        if not dates:
            return 0

        # Count consecutive days
        streak = 0
        today = datetime.utcnow().date()
        expected_date = today

        for activity_date in dates:
            if activity_date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif activity_date == expected_date + timedelta(days=1):
                # Yesterday counts too
                streak += 1
                expected_date = activity_date - timedelta(days=1)
            else:
                break

        return streak

    async def get_daily_breakdown(
        self,
        db: AsyncSession,
        child_id: str,
        days: int = 7,
    ) -> list[DailyStats]:
        """Get daily activity breakdown.

        Args:
            db: Database session
            child_id: Child ID
            days: Number of days

        Returns:
            List of DailyStats
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = select(
            func.date(PlayHistory.created_at).label("date"),
            func.count(PlayHistory.id).label("plays"),
            func.sum(PlayHistory.duration).label("duration"),
        ).where(
            PlayHistory.child_id == child_id,
            PlayHistory.created_at >= start_date,
        ).group_by(
            func.date(PlayHistory.created_at)
        ).order_by(
            func.date(PlayHistory.created_at)
        )

        result = await db.execute(query)
        daily_stats = []

        for row in result:
            daily_stats.append(DailyStats(
                date=row.date,
                total_plays=row.plays or 0,
                total_duration=row.duration or 0,
            ))

        return daily_stats
