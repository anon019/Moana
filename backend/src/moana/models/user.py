# src/moana/models/user.py
from typing import Any, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from moana.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for parent accounts."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    openid: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    unionid: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )
    nickname: Mapped[str] = mapped_column(
        String(100),
        default="",
        nullable=False,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize User with Python-side defaults."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid4())
        if "nickname" not in kwargs:
            kwargs["nickname"] = ""
        super().__init__(**kwargs)
