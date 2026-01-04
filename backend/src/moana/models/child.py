from datetime import date
from typing import Optional
from sqlalchemy import String, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from moana.models.base import Base, TimestampMixin


class Child(Base, TimestampMixin):
    """Child profile model."""

    __tablename__ = "children"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    favorite_characters: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    interests: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Parent reference (simplified for MVP)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    def age_in_months(self, reference_date: Optional[date] = None) -> int:
        """Calculate age in months from birth date."""
        ref = reference_date or date.today()
        months = (ref.year - self.birth_date.year) * 12
        months += ref.month - self.birth_date.month
        if ref.day < self.birth_date.day:
            months -= 1
        return max(0, months)
