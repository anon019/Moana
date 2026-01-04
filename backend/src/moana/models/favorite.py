# src/moana/models/favorite.py
from typing import Any
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from moana.models.base import Base, TimestampMixin


class Favorite(Base, TimestampMixin):
    """Favorite model for saved content."""

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_user_content_favorite"),
    )

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

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Favorite with Python-side defaults."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid4())
        super().__init__(**kwargs)
