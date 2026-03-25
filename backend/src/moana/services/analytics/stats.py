# src/moana/services/analytics/stats.py
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from moana.models import ContentType, PlayHistory


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


def _resolve_content_type(raw: object) -> Optional[ContentType]:
    """Normalize DB-stored content type to ContentType enum."""
    if raw is None:
        return None

    value = str(raw)
    if value.startswith("ContentType."):
        value = value.split(".", 1)[1]

    if not value:
        return None

    value = value.lower()
    try:
        return ContentType(value)
    except ValueError:
        name = value.upper()
        for item in ContentType:
            if item.name == name:
                return item
    return None


def _resolve_date(value: object) -> Optional[date]:
    """Normalize SQL date/datetime/string values to a date object."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return datetime.fromisoformat(str(value)).date()
    except (TypeError, ValueError):
        return None


def _session_duration_seconds(
    started_at: datetime,
    last_played_at: datetime | None,
    completed_at: datetime | None,
) -> int:
    if not started_at:
        return 0

    end_at = completed_at or last_played_at or started_at
    if end_at < started_at:
        return 0

    return int((end_at - started_at).total_seconds())


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

        result = await db.execute(
            select(
                PlayHistory.content_type,
                PlayHistory.content_id,
                PlayHistory.started_at,
                PlayHistory.last_played_at,
                PlayHistory.completed_at,
            ).where(
                PlayHistory.child_id == child_id,
                PlayHistory.started_at >= start_date,
            )
        )
        rows = result.all()

        total_plays = 0
        total_duration_seconds = 0

        type_stats: dict[ContentType, dict] = defaultdict(lambda: {
            "total_plays": 0,
            "total_duration": 0,
            "contents": set(),
        })

        for row in rows:
            ct = _resolve_content_type(row.content_type)
            if ct is None:
                continue

            total_plays += 1
            started_at = row.started_at
            duration = _session_duration_seconds(
                started_at,
                row.last_played_at,
                row.completed_at,
            )
            total_duration_seconds += duration

            entry = type_stats[ct]
            entry["total_plays"] += 1
            entry["total_duration"] += duration
            entry["contents"].add(row.content_id)

        content_stats: list[ContentStats] = []
        favorite_type: Optional[ContentType] = None
        max_plays = -1

        for ct, item in type_stats.items():
            cs = ContentStats(
                content_type=ct,
                total_plays=item["total_plays"],
                total_duration=item["total_duration"],
                unique_contents=len(item["contents"]),
            )
            content_stats.append(cs)

            if cs.total_plays > max_plays:
                max_plays = cs.total_plays
                favorite_type = ct

        if content_stats:
            content_stats.sort(key=lambda x: x.total_plays, reverse=True)

        last_activity_query = await db.execute(
            select(func.max(PlayHistory.started_at)).where(PlayHistory.child_id == child_id)
        )
        last_activity = last_activity_query.scalar_one_or_none()

        streak = await self._calculate_streak(db, child_id)

        return ChildStats(
            child_id=child_id,
            total_plays=total_plays,
            total_duration=total_duration_seconds,
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
        result = await db.execute(
            select(func.date(PlayHistory.started_at).label("activity_date"))
            .where(
                PlayHistory.child_id == child_id,
                PlayHistory.started_at >= datetime.utcnow() - timedelta(days=30),
            )
            .group_by(func.date(PlayHistory.started_at))
            .order_by(func.date(PlayHistory.started_at).desc())
        )

        activity_dates = set()
        for row in result:
            day = _resolve_date(row.activity_date)
            if day is not None:
                activity_dates.add(day)

        if not activity_dates:
            return 0

        today = datetime.utcnow().date()
        streak = 0
        cursor = today
        while cursor in activity_dates:
            streak += 1
            cursor -= timedelta(days=1)

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

        result = await db.execute(
            select(
                func.date(PlayHistory.started_at).label("activity_date"),
                PlayHistory.content_type,
                PlayHistory.started_at,
                PlayHistory.last_played_at,
                PlayHistory.completed_at,
            )
            .where(
                PlayHistory.child_id == child_id,
                PlayHistory.started_at >= start_date,
            )
            .order_by(func.date(PlayHistory.started_at))
        )

        rows = result.all()

        daily_map: dict[date, dict] = defaultdict(
            lambda: {
                "total_plays": 0,
                "total_duration": 0,
                "content_breakdown": defaultdict(int),
            }
        )

        for row in rows:
            date_value = _resolve_date(row.activity_date)
            if date_value is None:
                continue

            duration = _session_duration_seconds(
                row.started_at,
                row.last_played_at,
                row.completed_at,
            )

            ct = _resolve_content_type(row.content_type)
            content_type = ct.value if ct else str(row.content_type)

            daily_map[date_value]["total_plays"] += 1
            daily_map[date_value]["total_duration"] += duration
            daily_map[date_value]["content_breakdown"][content_type] += 1

        return [
            DailyStats(
                date=datetime.combine(day, datetime.min.time()),
                total_plays=item["total_plays"],
                total_duration=item["total_duration"],
                content_breakdown=dict(item["content_breakdown"]),
            )
            for day, item in sorted(daily_map.items())
        ]
