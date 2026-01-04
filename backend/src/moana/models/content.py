# src/moana/models/content.py
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, JSON, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

from moana.models.base import Base, TimestampMixin


class ContentType(str, Enum):
    """Content type enumeration."""
    PICTURE_BOOK = "picture_book"
    NURSERY_RHYME = "nursery_rhyme"
    VIDEO = "video"


# ThemeCategory 已改为自由字符串，不再限制枚举值
# 常见分类: habit(习惯养成), cognition(认知学习), emotion(情感发展),
#          social(社交能力), creativity(创造力), safety(安全教育), other(其他)


class ContentStatus(str, Enum):
    """Content generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class ReviewStatus(str, Enum):
    """Content moderation review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class AssetType(str, Enum):
    """Asset type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Content(Base, TimestampMixin):
    """Content model for picture books, nursery rhymes, videos."""

    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    child_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("children.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        SQLEnum(ContentType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    theme_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    theme_topic: Mapped[str] = mapped_column(String(100), nullable=False)

    # Personalization data
    personalization: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Content structure (pages for book, segments for video, etc.)
    content_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    status: Mapped[ContentStatus] = mapped_column(
        SQLEnum(ContentStatus, values_callable=lambda x: [e.value for e in x]),
        default=ContentStatus.PENDING,
        nullable=False,
    )

    # Content moderation
    review_status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReviewStatus.PENDING,
        nullable=False,
    )
    review_result: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Generation metadata
    generated_by: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Total duration in seconds (for audio/video content)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Nursery rhyme redesign fields
    user_selections: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="User-selected parameters for content generation"
    )
    user_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User's custom prompt (smart mode)"
    )
    enhanced_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Gemini-enhanced prompt sent to Suno"
    )
    all_tracks: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="All generated tracks from Suno (usually 2)"
    )

    # Relationships
    assets: Mapped[list["ContentAsset"]] = relationship(
        "ContentAsset",
        back_populates="content",
        cascade="all, delete-orphan",
    )


class ContentAsset(Base, TimestampMixin):
    """Individual asset (image, audio, video) for content."""

    __tablename__ = "content_assets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    content_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("contents.id"),
        nullable=False,
    )
    asset_type: Mapped[AssetType] = mapped_column(
        SQLEnum(AssetType),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # For ordering (page number, segment number, etc.)
    sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Duration in seconds (for audio/video)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Additional metadata (prompt, model used, etc.)
    asset_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationship
    content: Mapped["Content"] = relationship("Content", back_populates="assets")
