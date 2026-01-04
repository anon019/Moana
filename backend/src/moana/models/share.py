# src/moana/models/share.py
from enum import Enum
from typing import Any, Optional
from sqlalchemy import String, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
import secrets

from moana.models.base import Base, TimestampMixin


class SharePlatform(str, Enum):
    """Share platform enumeration."""
    WECHAT = "wechat"
    WECHAT_MOMENTS = "wechat_moments"
    QR_CODE = "qr_code"
    LINK = "link"


class Share(Base, TimestampMixin):
    """Share model for shared content."""

    __tablename__ = "shares"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    content_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("contents.id"),
        nullable=False,
        index=True,
    )
    platform: Mapped[SharePlatform] = mapped_column(
        SQLEnum(SharePlatform),
        nullable=False,
    )
    share_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    poster_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Share with Python-side defaults."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid4())
        if "share_code" not in kwargs:
            kwargs["share_code"] = secrets.token_urlsafe(16)
        if "view_count" not in kwargs:
            kwargs["view_count"] = 0
        super().__init__(**kwargs)
