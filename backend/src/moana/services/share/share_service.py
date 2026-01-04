# src/moana/services/share/share_service.py
from dataclasses import dataclass
from typing import Optional
import secrets

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from moana.models import Share, SharePlatform, Content


@dataclass
class ShareResult:
    """Result of share creation."""
    share_id: str
    share_code: str
    share_url: str
    poster_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "share_id": self.share_id,
            "share_code": self.share_code,
            "share_url": self.share_url,
            "poster_url": self.poster_url,
        }


class ShareService:
    """Service for managing content shares."""

    BASE_URL = "https://moana.example.com/share"

    async def create_share(
        self,
        db: AsyncSession,
        user_id: str,
        content_id: str,
        platform: SharePlatform,
        poster_url: Optional[str] = None,
    ) -> ShareResult:
        """Create a new share.

        Args:
            db: Database session
            user_id: User ID creating the share
            content_id: Content ID to share
            platform: Share platform
            poster_url: Optional poster image URL

        Returns:
            ShareResult with share details
        """
        share = Share(
            user_id=user_id,
            content_id=content_id,
            platform=platform,
            poster_url=poster_url,
        )

        db.add(share)
        await db.commit()
        await db.refresh(share)

        share_url = f"{self.BASE_URL}/{share.share_code}"

        return ShareResult(
            share_id=share.id,
            share_code=share.share_code,
            share_url=share_url,
            poster_url=poster_url,
        )

    async def get_share_by_code(
        self,
        db: AsyncSession,
        share_code: str,
    ) -> Optional[Share]:
        """Get share by share code.

        Args:
            db: Database session
            share_code: Share code

        Returns:
            Share or None if not found
        """
        result = await db.execute(
            select(Share).where(Share.share_code == share_code)
        )
        return result.scalar_one_or_none()

    async def increment_view_count(
        self,
        db: AsyncSession,
        share_code: str,
    ) -> bool:
        """Increment view count for a share.

        Args:
            db: Database session
            share_code: Share code

        Returns:
            True if successful, False otherwise
        """
        result = await db.execute(
            update(Share)
            .where(Share.share_code == share_code)
            .values(view_count=Share.view_count + 1)
        )
        await db.commit()
        return result.rowcount > 0

    async def get_user_shares(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Share]:
        """Get shares by user.

        Args:
            db: Database session
            user_id: User ID
            limit: Max number of shares
            offset: Offset for pagination

        Returns:
            List of shares
        """
        result = await db.execute(
            select(Share)
            .where(Share.user_id == user_id)
            .order_by(Share.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
