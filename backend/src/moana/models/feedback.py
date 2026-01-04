# src/moana/models/feedback.py
"""Feedback model for user feedback submission."""
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from moana.models.base import Base, TimestampMixin


class FeedbackType(str, Enum):
    """Type of feedback."""

    BUG = "bug"
    CONTENT = "content"
    SUGGEST = "suggest"
    OTHER = "other"


class FeedbackStatus(str, Enum):
    """Status of feedback."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


class Feedback(Base, TimestampMixin):
    """Feedback model for user submissions."""

    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    type: Mapped[FeedbackType] = mapped_column(
        String(20),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    contact: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[FeedbackStatus] = mapped_column(
        String(20),
        nullable=False,
        default=FeedbackStatus.PENDING,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Feedback with Python-side defaults."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid4())
        if "status" not in kwargs:
            kwargs["status"] = FeedbackStatus.PENDING
        super().__init__(**kwargs)
