# src/moana/api/play.py
"""Play API - 播放历史和答题记录相关端点."""
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Integer, and_, or_, select, func, case, cast
from sqlalchemy.ext.asyncio import AsyncSession

from moana.config import get_settings
from moana.database import get_db
from moana.models.child import Child
from moana.models.content import Content
from moana.models.play_history import PlayHistory, InteractionRecord
from moana.models.user import User
from moana.routers.auth import get_current_user

router = APIRouter()


# ========== Request/Response Schemas ==========


class StartPlayRequest(BaseModel):
    """开始播放请求."""
    child_id: str = Field(description="Child ID")
    content_id: str = Field(description="Content ID")
    content_type: Literal["picture_book", "nursery_rhyme", "video"] = Field(
        description="Content type"
    )
    # Optional: auto-fetched from content if not provided
    total_pages: int | None = Field(
        default=None,
        ge=1,
        description="Total pages/segments (auto-detected if not provided)",
    )


class StartPlayResponse(BaseModel):
    """开始播放响应."""
    play_history_id: str
    current_page: int
    completion_rate: float
    is_resumed: bool  # 是否断点续播


class UpdateProgressRequest(BaseModel):
    """更新进度请求."""
    play_history_id: str = Field(description="Play history ID")
    current_page: int = Field(ge=1, description="Current page number")


class UpdateProgressResponse(BaseModel):
    """更新进度响应."""
    completion_rate: float


class CompletePlayRequest(BaseModel):
    """完成播放请求."""
    play_history_id: str = Field(description="Play history ID")


class CompletePlayResponse(BaseModel):
    """完成播放响应."""
    completed_at: str
    total_time_seconds: float


class PlayHistoryItem(BaseModel):
    """播放历史项."""
    id: str
    content_id: str
    content_type: str
    current_page: int
    total_pages: int
    completion_rate: float
    started_at: str
    last_played_at: str
    completed_at: str | None
    is_completed: bool


class PlayHistoryListResponse(BaseModel):
    """播放历史列表响应."""
    items: list[PlayHistoryItem]
    total: int
    has_more: bool
    next_cursor: str | None = None


class SubmitInteractionRequest(BaseModel):
    """提交答题结果请求."""
    play_history_id: str = Field(description="Play history ID")
    page_num: int = Field(ge=1, description="Page number of the question")
    question_type: Literal["tap_count", "choice", "tap_object"] = Field(
        description="Question type"
    )
    is_correct: bool = Field(description="Whether answer is correct")
    attempts: int = Field(ge=1, default=1, description="Number of attempts")
    time_spent_ms: int = Field(ge=0, description="Time spent in milliseconds")


class SubmitInteractionResponse(BaseModel):
    """提交答题结果响应."""
    interaction_id: str


class PlayStatsResponse(BaseModel):
    """答题统计响应."""
    total_questions: int
    correct_count: int
    accuracy_rate: float
    by_type: dict[str, dict]  # 按题型统计


class DailyActivity(BaseModel):
    """Daily activity record."""
    date: str
    duration_minutes: int
    contents_count: int


class ThemeStats(BaseModel):
    """Theme statistics."""
    theme: str
    count: int


class LearningStatsPeriod(BaseModel):
    """Learning stats period info."""
    start_date: str
    end_date: str
    days: int


class LearningStatsSummary(BaseModel):
    """Learning stats summary."""
    total_duration_minutes: int
    total_books: int
    total_songs: int
    total_videos: int
    streak_days: int
    interaction_rate: float


class LearningStatsResponse(BaseModel):
    """Learning statistics response."""
    period: LearningStatsPeriod
    summary: LearningStatsSummary
    daily_activity: list[DailyActivity]
    top_themes: list[ThemeStats]


VALID_CONTENT_TYPES = {"picture_book", "nursery_rhyme", "video"}


async def _get_admin_user_id(db: AsyncSession) -> str | None:
    settings = get_settings()
    admin_openid = settings.admin_openid
    if not admin_openid:
        return None

    admin_user_id = await db.scalar(select(User.id).where(User.openid == admin_openid))
    return admin_user_id


async def _get_accessible_child(
    db: AsyncSession,
    child_id: str,
    current_user: User,
) -> Child | None:
    """获取用户可访问的宝贝（家庭共享模式）.

    用户可以访问：
    1. 自己创建的宝贝
    2. 管理员创建的宝贝（家庭共享）
    """
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        return None

    if child.parent_id == current_user.id:
        return child

    admin_user_id = await _get_admin_user_id(db)
    if admin_user_id and child.parent_id == admin_user_id:
        return child

    return None


def _normalize_content_type(raw: object | None) -> str:
    """Normalize stored content type to API string constants."""
    if raw is None:
        return ""

    value = str(raw)
    if value.startswith("ContentType."):
        value = value.split(".", 1)[1]

    return value.lower()


def _resolve_total_pages(content_type: str, content_data: dict, provided: int | None) -> int:
    if provided:
        return max(1, provided)

    if not isinstance(content_data, dict):
        return 1

    total_pages = 1
    if content_type == "picture_book":
        pages = content_data.get("pages") or []
        total_pages = len(pages) if isinstance(pages, (list, tuple)) else 1
    elif content_type == "video":
        clips = content_data.get("clips") or []
        total_pages = len(clips) if isinstance(clips, (list, tuple)) else 1
    elif content_type == "nursery_rhyme":
        total_pages = 1

    return max(1, total_pages)


def _duration_minutes(started_at: datetime | None, last_played_at: datetime | None, completed_at: datetime | None) -> int:
    if started_at is None:
        return 0

    end_time = completed_at or last_played_at or started_at
    if end_time < started_at:
        return 0

    return int((end_time - started_at).total_seconds() // 60)


def _encode_play_history_cursor(last_played_at: datetime, history_id: str) -> str:
    return f"{last_played_at.isoformat()}|{history_id}"


def _decode_play_history_cursor(cursor: str) -> tuple[datetime, str]:
    cursor_ts_str, cursor_id = cursor.split("|", 1)
    cursor_ts = datetime.fromisoformat(cursor_ts_str.replace("Z", "+00:00"))
    if cursor_ts.tzinfo is None:
        cursor_ts = cursor_ts.replace(tzinfo=timezone.utc)
    if not cursor_id:
        raise ValueError
    return cursor_ts, cursor_id


def _coerce_date(value: object | None) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _normalize_cursor_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _session_duration_minutes_expr(dialect_name: str):
    # Keep duration aggregation in SQL so learning-stats does not scan every
    # session row in Python for common date-range requests.
    end_time = func.coalesce(
        PlayHistory.completed_at,
        PlayHistory.last_played_at,
        PlayHistory.started_at,
    )

    if dialect_name == "sqlite":
        duration_seconds = (
            func.strftime("%s", end_time) - func.strftime("%s", PlayHistory.started_at)
        )
        return cast(
            case((duration_seconds > 0, duration_seconds / 60), else_=0),
            Integer,
        )

    duration_seconds = func.extract("epoch", end_time - PlayHistory.started_at)
    return cast(func.greatest(duration_seconds, 0) / 60, Integer)


# ========== API Endpoints ==========


@router.post("/start", response_model=StartPlayResponse)
async def start_play(
    request: StartPlayRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StartPlayResponse:
    """开始播放内容.

    如果已有未完成的播放记录，返回断点位置（断点续播）。
    """
    child = await _get_accessible_child(db, request.child_id, current_user)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    result = await db.execute(select(Content).where(Content.id == request.content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.content_type.value != request.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content type mismatch",
        )

    existing = await db.execute(
        select(PlayHistory)
        .where(
            PlayHistory.child_id == child.id,
            PlayHistory.content_id == request.content_id,
            PlayHistory.completed_at.is_(None),
        )
        .order_by(PlayHistory.last_played_at.desc())
        .limit(1)
    )
    last_history = existing.scalar_one_or_none()
    if last_history:
        return StartPlayResponse(
            play_history_id=last_history.id,
            current_page=last_history.current_page,
            completion_rate=last_history.completion_rate,
            is_resumed=True,
        )

    content_data = content.content_data or {}
    total_pages = _resolve_total_pages(
        content_type=request.content_type,
        content_data=content_data,
        provided=request.total_pages,
    )

    play = PlayHistory(
        child_id=child.id,
        content_id=request.content_id,
        content_type=request.content_type,
        total_pages=total_pages,
    )
    db.add(play)
    await db.commit()
    await db.refresh(play)

    return StartPlayResponse(
        play_history_id=play.id,
        current_page=play.current_page,
        completion_rate=play.completion_rate,
        is_resumed=False,
    )


@router.post("/progress", response_model=UpdateProgressResponse)
async def update_progress(
    request: UpdateProgressRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UpdateProgressResponse:
    """更新播放进度."""
    result = await db.execute(
        select(PlayHistory).where(PlayHistory.id == request.play_history_id)
    )
    play_history = result.scalar_one_or_none()

    if not play_history:
        raise HTTPException(status_code=404, detail="Play history not found")

    if not await _get_accessible_child(db, play_history.child_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Play history not found",
        )

    if play_history.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Play already completed",
        )

    if request.current_page > play_history.total_pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current page exceeds total pages",
        )

    play_history.update_progress(request.current_page)
    await db.commit()
    await db.refresh(play_history)

    return UpdateProgressResponse(completion_rate=play_history.completion_rate)


@router.post("/complete", response_model=CompletePlayResponse)
async def complete_play(
    request: CompletePlayRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompletePlayResponse:
    """完成播放."""
    result = await db.execute(
        select(PlayHistory).where(PlayHistory.id == request.play_history_id)
    )
    play_history = result.scalar_one_or_none()

    if not play_history:
        raise HTTPException(status_code=404, detail="Play history not found")

    if not await _get_accessible_child(db, play_history.child_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Play history not found",
        )

    if play_history.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Play already completed",
        )

    play_history.mark_completed()
    await db.commit()
    await db.refresh(play_history)

    return CompletePlayResponse(
        completed_at=play_history.completed_at.isoformat(),
        total_time_seconds=play_history.total_time_seconds,
    )


@router.get("/history/{child_id}", response_model=PlayHistoryListResponse)
async def get_play_history(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
    offset: int = 0,
    cursor: str | None = None,
    content_type: str | None = None,
) -> PlayHistoryListResponse:
    """获取播放历史列表."""
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be greater than 0",
        )
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must not exceed 100",
        )
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="offset must be greater than or equal to 0",
        )
    if cursor is not None and offset != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cursor and offset cannot be used together",
        )

    child = await _get_accessible_child(db, child_id, current_user)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    if content_type is not None and content_type not in VALID_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type",
        )

    base_filters = [PlayHistory.child_id == child_id]
    if content_type:
        base_filters.append(PlayHistory.content_type == content_type)

    dialect_name = db.bind.dialect.name if getattr(db, "bind", None) is not None else ""
    use_python_cursor = bool(cursor and dialect_name == "sqlite")

    page_filters = list(base_filters)
    cursor_ts = None
    cursor_id = None
    if cursor:
        try:
            cursor_ts, cursor_id = _decode_play_history_cursor(cursor)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cursor format. expected iso_datetime|history_id",
            ) from exc

        if not use_python_cursor:
            query_cursor_ts = cursor_ts
            page_filters.append(
                or_(
                    PlayHistory.last_played_at < query_cursor_ts,
                    and_(
                        PlayHistory.last_played_at == query_cursor_ts,
                        PlayHistory.id < cursor_id,
                    ),
                )
            )

    count_result = await db.execute(
        select(func.count()).select_from(PlayHistory).where(*base_filters)
    )
    total = int(count_result.scalar_one() or 0)

    query = (
        select(PlayHistory)
        .where(*(base_filters if use_python_cursor else page_filters))
        .order_by(
            PlayHistory.last_played_at.desc(),
            PlayHistory.id.desc(),
        )
    )
    if not use_python_cursor:
        query = query.limit(limit + 1)
    if offset:
        query = query.offset(offset)

    result = await db.execute(query)
    records = list(result.scalars().all())

    if use_python_cursor and cursor_ts is not None and cursor_id is not None:
        normalized_cursor_ts = _normalize_cursor_datetime(cursor_ts)
        records = [
            record
            for record in records
            if (
                _normalize_cursor_datetime(record.last_played_at) < normalized_cursor_ts
                or (
                    _normalize_cursor_datetime(record.last_played_at) == normalized_cursor_ts
                    and record.id < cursor_id
                )
            )
        ]
        records = records[: limit + 1]

    next_cursor = None
    has_more = len(records) > limit
    if has_more:
        records = records[:limit]
        last_record = records[-1]
        next_cursor = _encode_play_history_cursor(last_record.last_played_at, last_record.id)

    return PlayHistoryListResponse(
        items=[
            PlayHistoryItem(
                id=record.id,
                content_id=record.content_id,
                content_type=_normalize_content_type(record.content_type),
                current_page=record.current_page,
                total_pages=record.total_pages,
                completion_rate=record.completion_rate,
                started_at=record.started_at.isoformat(),
                last_played_at=record.last_played_at.isoformat(),
                completed_at=record.completed_at.isoformat() if record.completed_at else None,
                is_completed=record.is_completed,
            )
            for record in records
        ],
        total=total,
        has_more=has_more,
        next_cursor=next_cursor,
    )


@router.post("/interaction", response_model=SubmitInteractionResponse)
async def submit_interaction(
    request: SubmitInteractionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubmitInteractionResponse:
    """提交答题结果."""
    result = await db.execute(
        select(PlayHistory).where(PlayHistory.id == request.play_history_id)
    )
    play_history = result.scalar_one_or_none()

    if not play_history:
        raise HTTPException(status_code=404, detail="Play history not found")

    if not await _get_accessible_child(db, play_history.child_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Play history not found",
        )

    if request.page_num > play_history.total_pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question page exceeds total pages",
        )

    interaction = InteractionRecord(
        play_history_id=request.play_history_id,
        page_num=request.page_num,
        question_type=request.question_type,
        is_correct=request.is_correct,
        attempts=request.attempts,
        time_spent_ms=request.time_spent_ms,
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)

    return SubmitInteractionResponse(interaction_id=interaction.id)


@router.get("/stats/{child_id}", response_model=PlayStatsResponse)
async def get_play_stats(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlayStatsResponse:
    """获取答题统计."""
    child = await _get_accessible_child(db, child_id, current_user)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    total_row = await db.execute(
        select(
            func.count(InteractionRecord.id).label("total_questions"),
            func.coalesce(
                func.sum(case((InteractionRecord.is_correct.is_(True), 1), else_=0)),
                0,
            ).label("correct_count"),
        )
        .join(PlayHistory, InteractionRecord.play_history_id == PlayHistory.id)
        .where(PlayHistory.child_id == child.id)
    )
    total = total_row.one()

    total_questions = int(total.total_questions or 0)
    correct_count = int(total.correct_count or 0)

    by_type_query = await db.execute(
        select(
            InteractionRecord.question_type.label("question_type"),
            func.count(InteractionRecord.id).label("total"),
            func.coalesce(
                func.sum(case((InteractionRecord.is_correct.is_(True), 1), else_=0)),
                0,
            ).label("correct"),
        )
        .join(PlayHistory, InteractionRecord.play_history_id == PlayHistory.id)
        .where(PlayHistory.child_id == child.id)
        .group_by(InteractionRecord.question_type)
    )
    by_type_rows = by_type_query.all()

    by_type: dict[str, dict] = {}
    for row in by_type_rows:
        total_by_type = int(row.total or 0)
        correct_by_type = int(row.correct or 0)
        by_type[row.question_type] = {
            "total": total_by_type,
            "correct": correct_by_type,
            "accuracy_rate": correct_by_type / total_by_type if total_by_type > 0 else 0.0,
        }

    return PlayStatsResponse(
        total_questions=total_questions,
        correct_count=correct_count,
        accuracy_rate=correct_count / total_questions if total_questions > 0 else 0.0,
        by_type=by_type,
    )


@router.get("/learning-stats/{child_id}", response_model=LearningStatsResponse)
async def get_learning_stats(
    child_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = 7,
) -> LearningStatsResponse:
    """Get detailed learning statistics for a child.

    Returns aggregated learning data for the specified period (default 7 days).
    """
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days must be greater than 0",
        )
    if days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days must not exceed 365",
        )

    child = await _get_accessible_child(db, child_id, current_user)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    now = datetime.now(timezone.utc)
    today = now.date()
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)

    duration_minutes_expr = _session_duration_minutes_expr(db.bind.dialect.name)
    activity_date_expr = func.date(PlayHistory.started_at).label("activity_date")

    daily_result = await db.execute(
        select(
            activity_date_expr,
            func.coalesce(func.sum(duration_minutes_expr), 0).label("duration_minutes"),
            func.count(PlayHistory.id).label("contents_count"),
        )
        .where(
            PlayHistory.child_id == child.id,
            PlayHistory.started_at >= start_dt,
        )
        .group_by(activity_date_expr)
        .order_by(activity_date_expr.asc())
    )
    daily_rows = daily_result.all()

    summary_result = await db.execute(
        select(
            func.coalesce(
                func.sum(case((PlayHistory.content_type == "picture_book", 1), else_=0)),
                0,
            ).label("total_books"),
            func.coalesce(
                func.sum(case((PlayHistory.content_type == "nursery_rhyme", 1), else_=0)),
                0,
            ).label("total_songs"),
            func.coalesce(
                func.sum(case((PlayHistory.content_type == "video", 1), else_=0)),
                0,
            ).label("total_videos"),
        )
        .where(PlayHistory.child_id == child.id, PlayHistory.started_at >= start_dt)
    )
    summary_row = summary_result.one()

    daily_map: dict[date, dict[str, int]] = {}
    total_books = int(summary_row.total_books or 0)
    total_songs = int(summary_row.total_songs or 0)
    total_videos = int(summary_row.total_videos or 0)
    total_duration_minutes = 0
    activity_dates: set[date] = set()

    for row in daily_rows:
        activity_date = _coerce_date(row.activity_date)
        if activity_date is None:
            continue

        duration_minutes = int(row.duration_minutes or 0)
        contents_count = int(row.contents_count or 0)
        daily_map[activity_date] = {
            "duration_minutes": duration_minutes,
            "count": contents_count,
        }
        activity_dates.add(activity_date)
        total_duration_minutes += duration_minutes

    streak_days = 0
    cursor = today
    while cursor >= start_date:
        if cursor in activity_dates:
            streak_days += 1
            cursor -= timedelta(days=1)
        else:
            break

    # Daily breakdown for each day in range
    daily_activity: list[DailyActivity] = []
    for offset_day in range(days):
        date_obj = today - timedelta(days=offset_day)
        data = daily_map.get(date_obj, {"duration_minutes": 0, "count": 0})
        daily_activity.append(DailyActivity(
            date=date_obj.isoformat(),
            duration_minutes=int(data["duration_minutes"]),
            contents_count=int(data["count"]),
        ))

    interaction_query = await db.execute(
        select(
            func.count(InteractionRecord.id).label("total_interactions"),
            func.coalesce(
                func.sum(case((InteractionRecord.is_correct.is_(True), 1), else_=0)),
                0,
            ).label("correct_interactions"),
        )
        .join(PlayHistory, InteractionRecord.play_history_id == PlayHistory.id)
        .where(PlayHistory.child_id == child.id)
        .where(PlayHistory.started_at >= start_dt)
    )
    interaction_row = interaction_query.one()
    total_interactions = int(interaction_row.total_interactions or 0)
    correct_interactions = int(interaction_row.correct_interactions or 0)
    interaction_rate = (
        correct_interactions / total_interactions if total_interactions > 0 else 0.0
    )

    themes_query = await db.execute(
        select(
            Content.theme_topic,
            func.count(PlayHistory.id).label("count"),
        )
        .join(PlayHistory, Content.id == PlayHistory.content_id)
        .where(
            PlayHistory.child_id == child.id,
            PlayHistory.started_at >= start_dt,
            Content.theme_topic.is_not(None),
            Content.theme_topic != "",
        )
        .group_by(Content.theme_topic)
        .order_by(func.count(PlayHistory.id).desc())
        .limit(3)
    )

    top_themes = [
        ThemeStats(theme=row.theme_topic, count=int(row.count or 0))
        for row in themes_query.all()
    ]

    summary = LearningStatsSummary(
        total_duration_minutes=total_duration_minutes,
        total_books=total_books,
        total_songs=total_songs,
        total_videos=total_videos,
        streak_days=streak_days,
        interaction_rate=round(interaction_rate, 2),
    )

    return LearningStatsResponse(
        period=LearningStatsPeriod(
            start_date=start_date.isoformat(),
            end_date=today.isoformat(),
            days=days,
        ),
        summary=summary,
        daily_activity=daily_activity,
        top_themes=top_themes,
    )
