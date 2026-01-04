# src/moana/api/play.py
"""Play API - 播放历史和答题记录相关端点."""
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from moana.database import get_db
from moana.models.content import Content

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
    total_pages: Optional[int] = Field(default=None, ge=1, description="Total pages/segments (auto-detected if not provided)")


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


# ========== 内存存储（MVP 阶段，后续替换为数据库） ==========

_play_histories: dict[str, dict] = {}
_interactions: dict[str, dict] = {}


# ========== API Endpoints ==========

@router.post("/start", response_model=StartPlayResponse)
async def start_play(
    request: StartPlayRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """开始播放内容.

    如果已有未完成的播放记录，返回断点位置（断点续播）。
    total_pages 可选，如果不传则自动从内容数据中获取。
    """
    # 查找未完成的播放记录
    for ph_id, ph in _play_histories.items():
        if (ph["child_id"] == request.child_id and
            ph["content_id"] == request.content_id and
            ph["completed_at"] is None):
            # 断点续播
            return StartPlayResponse(
                play_history_id=ph_id,
                current_page=ph["current_page"],
                completion_rate=ph["completion_rate"],
                is_resumed=True,
            )

    # 获取 total_pages
    total_pages = request.total_pages
    if total_pages is None:
        # Auto-fetch from content
        result = await db.execute(
            select(Content).where(Content.id == request.content_id)
        )
        content = result.scalar_one_or_none()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        content_data = content.content_data or {}
        if request.content_type == "picture_book":
            total_pages = len(content_data.get("pages", []))
        elif request.content_type == "nursery_rhyme":
            # Nursery rhyme is single-page
            total_pages = 1
        elif request.content_type == "video":
            total_pages = len(content_data.get("clips", [])) or 1
        else:
            total_pages = 1

        if total_pages == 0:
            total_pages = 1  # Minimum 1 page

    # 创建新记录
    play_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    _play_histories[play_id] = {
        "id": play_id,
        "child_id": request.child_id,
        "content_id": request.content_id,
        "content_type": request.content_type,
        "current_page": 1,
        "total_pages": total_pages,
        "completion_rate": 0.0,
        "started_at": now,
        "last_played_at": now,
        "completed_at": None,
    }

    return StartPlayResponse(
        play_history_id=play_id,
        current_page=1,
        completion_rate=0.0,
        is_resumed=False,
    )


@router.post("/progress", response_model=UpdateProgressResponse)
async def update_progress(request: UpdateProgressRequest):
    """更新播放进度."""
    ph = _play_histories.get(request.play_history_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Play history not found")

    if ph["completed_at"]:
        raise HTTPException(status_code=400, detail="Play already completed")

    # 更新进度
    ph["current_page"] = request.current_page
    ph["completion_rate"] = request.current_page / ph["total_pages"]
    ph["last_played_at"] = datetime.now().isoformat()

    return UpdateProgressResponse(completion_rate=ph["completion_rate"])


@router.post("/complete", response_model=CompletePlayResponse)
async def complete_play(request: CompletePlayRequest):
    """完成播放."""
    ph = _play_histories.get(request.play_history_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Play history not found")

    if ph["completed_at"]:
        raise HTTPException(status_code=400, detail="Play already completed")

    # 标记完成
    now = datetime.now()
    ph["current_page"] = ph["total_pages"]
    ph["completion_rate"] = 1.0
    ph["completed_at"] = now.isoformat()
    ph["last_played_at"] = now.isoformat()

    # 计算总时长
    started = datetime.fromisoformat(ph["started_at"])
    total_seconds = (now - started).total_seconds()

    return CompletePlayResponse(
        completed_at=ph["completed_at"],
        total_time_seconds=total_seconds,
    )


@router.get("/history/{child_id}", response_model=PlayHistoryListResponse)
async def get_play_history(
    child_id: str,
    limit: int = 20,
    offset: int = 0,
    content_type: str | None = None,
):
    """获取播放历史列表."""
    # 过滤
    items = [
        ph for ph in _play_histories.values()
        if ph["child_id"] == child_id
        and (content_type is None or ph["content_type"] == content_type)
    ]

    # 按最后播放时间排序
    items.sort(key=lambda x: x["last_played_at"], reverse=True)

    total = len(items)
    items = items[offset:offset + limit]

    return PlayHistoryListResponse(
        items=[
            PlayHistoryItem(
                id=ph["id"],
                content_id=ph["content_id"],
                content_type=ph["content_type"],
                current_page=ph["current_page"],
                total_pages=ph["total_pages"],
                completion_rate=ph["completion_rate"],
                started_at=ph["started_at"],
                last_played_at=ph["last_played_at"],
                completed_at=ph["completed_at"],
                is_completed=ph["completed_at"] is not None,
            )
            for ph in items
        ],
        total=total,
        has_more=offset + limit < total,
    )


@router.post("/interaction", response_model=SubmitInteractionResponse)
async def submit_interaction(request: SubmitInteractionRequest):
    """提交答题结果."""
    ph = _play_histories.get(request.play_history_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Play history not found")

    # 创建答题记录
    interaction_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    _interactions[interaction_id] = {
        "id": interaction_id,
        "play_history_id": request.play_history_id,
        "child_id": ph["child_id"],
        "page_num": request.page_num,
        "question_type": request.question_type,
        "is_correct": request.is_correct,
        "attempts": request.attempts,
        "time_spent_ms": request.time_spent_ms,
        "answered_at": now,
    }

    return SubmitInteractionResponse(interaction_id=interaction_id)


@router.get("/stats/{child_id}", response_model=PlayStatsResponse)
async def get_play_stats(child_id: str):
    """获取答题统计."""
    # 过滤该孩子的答题记录
    child_interactions = [
        i for i in _interactions.values()
        if i["child_id"] == child_id
    ]

    total = len(child_interactions)
    correct = sum(1 for i in child_interactions if i["is_correct"])

    # 按题型统计
    by_type: dict[str, dict] = {}
    for i in child_interactions:
        qt = i["question_type"]
        if qt not in by_type:
            by_type[qt] = {"total": 0, "correct": 0}
        by_type[qt]["total"] += 1
        if i["is_correct"]:
            by_type[qt]["correct"] += 1

    # 计算正确率
    for qt in by_type:
        t = by_type[qt]["total"]
        c = by_type[qt]["correct"]
        by_type[qt]["accuracy_rate"] = c / t if t > 0 else 0.0

    return PlayStatsResponse(
        total_questions=total,
        correct_count=correct,
        accuracy_rate=correct / total if total > 0 else 0.0,
        by_type=by_type,
    )


@router.get("/learning-stats/{child_id}", response_model=LearningStatsResponse)
async def get_learning_stats(
    child_id: str,
    days: int = 7,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Get detailed learning statistics for a child.

    Returns aggregated learning data for the specified period (default 7 days).
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)

    # Filter play histories for this child in date range
    child_histories = [
        ph for ph in _play_histories.values()
        if ph["child_id"] == child_id
    ]

    # Filter by date range
    histories_in_range = []
    for ph in child_histories:
        ph_date = datetime.fromisoformat(ph["started_at"]).date()
        if start_date <= ph_date <= today:
            histories_in_range.append(ph)

    # Calculate totals by content type
    total_books = sum(1 for ph in histories_in_range if ph["content_type"] == "picture_book")
    total_songs = sum(1 for ph in histories_in_range if ph["content_type"] == "nursery_rhyme")
    total_videos = sum(1 for ph in histories_in_range if ph["content_type"] == "video")

    # Calculate total duration (estimate from completed sessions)
    total_duration = 0
    for ph in histories_in_range:
        if ph["completed_at"]:
            started = datetime.fromisoformat(ph["started_at"])
            completed = datetime.fromisoformat(ph["completed_at"])
            total_duration += int((completed - started).total_seconds() / 60)
        else:
            # Estimate 5 minutes per incomplete session
            total_duration += 5

    # Calculate daily activity
    daily_data: dict[str, dict] = defaultdict(lambda: {"duration": 0, "count": 0})
    for ph in histories_in_range:
        ph_date = datetime.fromisoformat(ph["started_at"]).date().isoformat()
        daily_data[ph_date]["count"] += 1
        if ph["completed_at"]:
            started = datetime.fromisoformat(ph["started_at"])
            completed = datetime.fromisoformat(ph["completed_at"])
            daily_data[ph_date]["duration"] += int((completed - started).total_seconds() / 60)
        else:
            daily_data[ph_date]["duration"] += 5

    # Build daily_activity list (all days in range, even if no activity)
    daily_activity = []
    for i in range(days):
        date = (today - timedelta(days=i)).isoformat()
        data = daily_data.get(date, {"duration": 0, "count": 0})
        daily_activity.append(DailyActivity(
            date=date,
            duration_minutes=data["duration"],
            contents_count=data["count"],
        ))

    # Calculate streak days (consecutive days with activity from today backwards)
    streak_days = 0
    for i in range(days):
        date = (today - timedelta(days=i)).isoformat()
        if daily_data.get(date, {}).get("count", 0) > 0:
            streak_days += 1
        else:
            break

    # Get interaction rate from existing stats
    child_interactions = [
        i for i in _interactions.values()
        if i["child_id"] == child_id
    ]
    total_interactions = len(child_interactions)
    correct_interactions = sum(1 for i in child_interactions if i["is_correct"])
    interaction_rate = correct_interactions / total_interactions if total_interactions > 0 else 0.0

    # Get top themes (requires database query for content themes)
    theme_counts: dict[str, int] = defaultdict(int)
    content_ids = list(set(ph["content_id"] for ph in histories_in_range))

    if content_ids and db is not None:
        result = await db.execute(
            select(Content).where(Content.id.in_(content_ids))
        )
        contents = result.scalars().all()
        for content in contents:
            if content.theme_topic:
                theme_counts[content.theme_topic] += 1

    top_themes = sorted(
        [ThemeStats(theme=t, count=c) for t, c in theme_counts.items()],
        key=lambda x: x.count,
        reverse=True,
    )[:3]

    return LearningStatsResponse(
        period=LearningStatsPeriod(
            start_date=start_date.isoformat(),
            end_date=today.isoformat(),
            days=days,
        ),
        summary=LearningStatsSummary(
            total_duration_minutes=total_duration,
            total_books=total_books,
            total_songs=total_songs,
            total_videos=total_videos,
            streak_days=streak_days,
            interaction_rate=round(interaction_rate, 2),
        ),
        daily_activity=daily_activity,
        top_themes=top_themes,
    )
