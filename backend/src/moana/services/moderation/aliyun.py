# src/moana/services/moderation/aliyun.py
import httpx
from typing import Optional

from moana.config import get_settings
from moana.services.moderation.base import (
    ModerationService,
    ModerationResult,
    ModerationCategory,
)


class AliyunModerationService(ModerationService):
    """Aliyun content moderation service.

    Uses Aliyun Green (内容安全) API for content moderation.
    """

    TEXT_API = "https://green.cn-shanghai.aliyuncs.com/green/text/scan"
    IMAGE_API = "https://green.cn-shanghai.aliyuncs.com/green/image/scan"

    # Category mapping from Aliyun labels to our categories
    CATEGORY_MAP = {
        "porn": ModerationCategory.PORNOGRAPHY,
        "terrorism": ModerationCategory.TERRORISM,
        "politics": ModerationCategory.POLITICS,
        "abuse": ModerationCategory.ABUSE,
        "violence": ModerationCategory.VIOLENCE,
        "spam": ModerationCategory.SPAM,
        "ad": ModerationCategory.SPAM,
        "contraband": ModerationCategory.INAPPROPRIATE,
        "normal": ModerationCategory.SAFE,
    }

    def __init__(self):
        settings = get_settings()
        self.access_key = settings.oss_access_key
        self.secret_key = settings.oss_secret_key

    def _parse_text_result(self, response: dict) -> ModerationResult:
        """Parse Aliyun text moderation response."""
        try:
            data = response.get("data", [{}])[0]
            results = data.get("results", [])

            categories = []
            is_safe = True

            for result in results:
                label = result.get("label", "normal")
                suggestion = result.get("suggestion", "pass")

                if suggestion == "block":
                    is_safe = False
                    if label in self.CATEGORY_MAP:
                        categories.append(self.CATEGORY_MAP[label])

            return ModerationResult(
                is_safe=is_safe,
                categories=categories,
                raw_response=response,
            )
        except (KeyError, IndexError):
            # Default to safe if parsing fails
            return ModerationResult(
                is_safe=True,
                reason="Failed to parse moderation response",
                raw_response=response,
            )

    def _parse_image_result(self, response: dict) -> ModerationResult:
        """Parse Aliyun image moderation response."""
        try:
            data = response.get("data", [{}])[0]
            results = data.get("results", [])

            categories = []
            is_safe = True

            for result in results:
                label = result.get("label", "normal")
                suggestion = result.get("suggestion", "pass")

                if suggestion == "block":
                    is_safe = False
                    if label in self.CATEGORY_MAP:
                        categories.append(self.CATEGORY_MAP[label])

            return ModerationResult(
                is_safe=is_safe,
                categories=categories,
                raw_response=response,
            )
        except (KeyError, IndexError):
            return ModerationResult(
                is_safe=True,
                reason="Failed to parse moderation response",
                raw_response=response,
            )

    async def moderate_text(self, text: str) -> ModerationResult:
        """Check text content using Aliyun Green API."""
        if not self.access_key or not self.secret_key:
            # Skip moderation if not configured
            return ModerationResult(
                is_safe=True,
                reason="Moderation not configured",
            )

        # For MVP, return safe result (actual API integration would require signing)
        # TODO: Implement actual Aliyun API call with signature
        return ModerationResult(
            is_safe=True,
            reason="Moderation check skipped (MVP)",
        )

    async def moderate_image(self, image_url: str) -> ModerationResult:
        """Check image content using Aliyun Green API."""
        if not self.access_key or not self.secret_key:
            return ModerationResult(
                is_safe=True,
                reason="Moderation not configured",
            )

        # For MVP, return safe result
        # TODO: Implement actual Aliyun API call with signature
        return ModerationResult(
            is_safe=True,
            reason="Moderation check skipped (MVP)",
        )

    async def moderate_audio(self, audio_url: str) -> ModerationResult:
        """Check audio content using Aliyun Green API."""
        if not self.access_key or not self.secret_key:
            return ModerationResult(
                is_safe=True,
                reason="Moderation not configured",
            )

        # For MVP, return safe result
        # TODO: Implement actual Aliyun API call with signature
        return ModerationResult(
            is_safe=True,
            reason="Moderation check skipped (MVP)",
        )
