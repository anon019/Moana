"""播放历史和答题记录模型."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Boolean, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from moana.models.base import Base, TimestampMixin


class PlayHistory(Base, TimestampMixin):
    """播放历史记录.

    记录孩子观看内容的进度，支持断点续播。
    """

    __tablename__ = "play_histories"

    __table_args__ = (
        Index("ix_play_histories_child_started_at", "child_id", "started_at"),
        Index("ix_play_histories_child_last_played_at", "child_id", "last_played_at"),
        Index("ix_play_histories_child_content_type", "child_id", "content_type"),
        Index("ix_play_histories_child_content_completed_last_played", "child_id", "content_id", "completed_at", "last_played_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    child_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("children.id"),
        nullable=False,
        index=True,
    )
    content_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("contents.id"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # picture_book / nursery_rhyme / video

    # 进度追踪
    current_page: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    total_pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    completion_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # 时间记录
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 关系
    interactions: Mapped[list["InteractionRecord"]] = relationship(
        "InteractionRecord",
        back_populates="play_history",
        cascade="all, delete-orphan",
    )

    def update_progress(self, current_page: int) -> None:
        """更新播放进度."""
        self.current_page = current_page
        self.completion_rate = current_page / self.total_pages if self.total_pages > 0 else 0.0
        self.last_played_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """标记为已完成."""
        self.current_page = self.total_pages
        self.completion_rate = 1.0
        self.completed_at = datetime.now(timezone.utc)
        self.last_played_at = datetime.now(timezone.utc)

    @property
    def is_completed(self) -> bool:
        """是否已完成."""
        return self.completed_at is not None

    @property
    def total_time_seconds(self) -> float:
        """总播放时长（秒）."""
        end_time = self.completed_at or self.last_played_at
        return (end_time - self.started_at).total_seconds()


class InteractionRecord(Base, TimestampMixin):
    """答题记录.

    记录孩子在播放过程中的答题情况。
    """

    __tablename__ = "interaction_records"

    __table_args__ = (
        Index("ix_interaction_records_play_history_question_type", "play_history_id", "question_type"),
        Index("ix_interaction_records_play_history_is_correct", "play_history_id", "is_correct"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    play_history_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("play_histories.id"),
        nullable=False,
        index=True,
    )
    page_num: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    question_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # tap_count / choice / tap_object
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    time_spent_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 关系
    play_history: Mapped["PlayHistory"] = relationship(
        "PlayHistory",
        back_populates="interactions",
    )
