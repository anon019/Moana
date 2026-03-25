"""任务状态持久化模型."""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from moana.models.base import Base, TimestampMixin


class TaskStatus(Base, TimestampMixin):
    """Persisted async task status."""

    __tablename__ = "task_statuses"

    task_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )
    task_type: Mapped[str] = mapped_column(
        String(64),
        default="generic",
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    stage: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    message: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    content_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
