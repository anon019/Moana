# src/moana/models/child_settings.py
"""孩子端配置模型."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from moana.models.base import Base


class ChildSettings(Base):
    """孩子端配置.

    存储每个孩子的个性化设置，如观看限时、休息提醒等。
    """

    __tablename__ = "child_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
        unique=True,  # 一对一关系
        index=True,
    )

    # 观看限制
    daily_limit_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    session_limit_minutes: Mapped[int] = mapped_column(
        Integer,
        default=20,
        nullable=False,
    )
    rest_reminder_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # 时间戳
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @classmethod
    def get_defaults(cls) -> dict:
        """获取默认设置值."""
        return {
            "daily_limit_minutes": 60,
            "session_limit_minutes": 20,
            "rest_reminder_enabled": True,
        }
