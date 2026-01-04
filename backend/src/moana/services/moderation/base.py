# src/moana/services/moderation/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ModerationCategory(str, Enum):
    """Content moderation categories."""
    SAFE = "safe"
    VIOLENCE = "violence"
    PORNOGRAPHY = "pornography"
    POLITICS = "politics"
    TERRORISM = "terrorism"
    ABUSE = "abuse"
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"


@dataclass
class ModerationResult:
    """Result of content moderation check."""
    is_safe: bool
    categories: list[ModerationCategory] = field(default_factory=list)
    confidence: float = 1.0
    reason: Optional[str] = None
    raw_response: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_safe": self.is_safe,
            "categories": [c.value for c in self.categories],
            "confidence": self.confidence,
            "reason": self.reason,
        }


@dataclass
class ContentModerationRequest:
    """Request for content moderation."""
    text: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    content_id: Optional[str] = None


class ModerationService(ABC):
    """Abstract base class for moderation services."""

    @abstractmethod
    async def moderate_text(self, text: str) -> ModerationResult:
        """Check text content for policy violations.

        Args:
            text: The text to check

        Returns:
            ModerationResult with safety assessment
        """
        pass

    @abstractmethod
    async def moderate_image(self, image_url: str) -> ModerationResult:
        """Check image content for policy violations.

        Args:
            image_url: URL of the image to check

        Returns:
            ModerationResult with safety assessment
        """
        pass

    @abstractmethod
    async def moderate_audio(self, audio_url: str) -> ModerationResult:
        """Check audio content for policy violations.

        Args:
            audio_url: URL of the audio to check

        Returns:
            ModerationResult with safety assessment
        """
        pass

    async def moderate_content(
        self,
        request: ContentModerationRequest,
    ) -> ModerationResult:
        """Moderate content based on provided request.

        Checks all non-None content types and returns combined result.
        """
        results: list[ModerationResult] = []

        if request.text:
            results.append(await self.moderate_text(request.text))

        if request.image_url:
            results.append(await self.moderate_image(request.image_url))

        if request.audio_url:
            results.append(await self.moderate_audio(request.audio_url))

        if not results:
            return ModerationResult(is_safe=True)

        # Combine results: content is safe only if ALL checks pass
        is_safe = all(r.is_safe for r in results)
        categories = []
        reasons = []

        for r in results:
            categories.extend(r.categories)
            if r.reason:
                reasons.append(r.reason)

        return ModerationResult(
            is_safe=is_safe,
            categories=list(set(categories)),
            confidence=min(r.confidence for r in results),
            reason="; ".join(reasons) if reasons else None,
        )
