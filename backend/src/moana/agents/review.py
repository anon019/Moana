# src/moana/agents/review.py
from dataclasses import dataclass
from typing import Optional

from moana.services.llm.gemini import GeminiService
from moana.services.moderation import AliyunModerationService, ModerationResult


@dataclass
class ReviewResult:
    """Result of content review."""
    is_approved: bool
    moderation_result: ModerationResult
    ai_review: Optional[dict] = None
    suggestions: list[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_approved": self.is_approved,
            "moderation": self.moderation_result.to_dict(),
            "ai_review": self.ai_review,
            "suggestions": self.suggestions,
        }


REVIEW_SYSTEM_PROMPT = """你是一位专业的儿童内容审核专家，负责确保所有内容适合1-3岁幼儿。

审核标准：
1. 安全性：无暴力、恐怖、不适宜儿童的内容
2. 教育性：内容对幼儿有正向教育意义
3. 语言适宜性：用词简单、正向、无粗俗语言
4. 文化敏感性：尊重多元文化，无歧视内容
5. 年龄适宜性：复杂度适合目标年龄段

请对内容进行评估，输出JSON格式结果。"""


class ReviewAgent:
    """Agent for reviewing and moderating content."""

    def __init__(self):
        self._llm = GeminiService()
        self._moderation = AliyunModerationService()

    async def review_text(self, text: str) -> ReviewResult:
        """Review text content for children's appropriateness.

        Args:
            text: The text content to review

        Returns:
            ReviewResult with approval status and feedback
        """
        # First, run automated moderation
        moderation_result = await self._moderation.moderate_text(text)

        if not moderation_result.is_safe:
            return ReviewResult(
                is_approved=False,
                moderation_result=moderation_result,
                suggestions=["内容未通过自动审核，请修改后重新提交"],
            )

        # Then, run AI review for child-appropriateness
        prompt = f"""请审核以下儿童内容是否适合1-3岁幼儿：

内容：
{text}

请评估并输出JSON格式：
{{
  "is_appropriate": true/false,
  "age_suitable": true/false,
  "language_quality": "good/fair/poor",
  "educational_value": "high/medium/low",
  "concerns": ["concern1", "concern2"],
  "suggestions": ["suggestion1", "suggestion2"]
}}"""

        try:
            response = await self._llm.generate(
                prompt=prompt,
                system_prompt=REVIEW_SYSTEM_PROMPT,
                temperature=0.3,
            )

            # Try to parse as JSON
            import json
            ai_review = json.loads(response)

            is_approved = (
                ai_review.get("is_appropriate", True) and
                ai_review.get("age_suitable", True)
            )

            return ReviewResult(
                is_approved=is_approved,
                moderation_result=moderation_result,
                ai_review=ai_review,
                suggestions=ai_review.get("suggestions", []),
            )
        except (json.JSONDecodeError, Exception):
            # If AI review fails, rely on moderation result
            return ReviewResult(
                is_approved=moderation_result.is_safe,
                moderation_result=moderation_result,
                suggestions=[],
            )

    async def review_image(self, image_url: str) -> ReviewResult:
        """Review image content.

        Args:
            image_url: URL of the image to review

        Returns:
            ReviewResult with approval status
        """
        moderation_result = await self._moderation.moderate_image(image_url)

        return ReviewResult(
            is_approved=moderation_result.is_safe,
            moderation_result=moderation_result,
        )

    async def review_content(
        self,
        text: Optional[str] = None,
        image_urls: Optional[list[str]] = None,
        audio_url: Optional[str] = None,
    ) -> ReviewResult:
        """Review complete content with text, images, and audio.

        Args:
            text: Text content to review
            image_urls: List of image URLs to review
            audio_url: Audio URL to review

        Returns:
            Combined ReviewResult
        """
        results: list[ReviewResult] = []

        if text:
            results.append(await self.review_text(text))

        if image_urls:
            for url in image_urls:
                results.append(await self.review_image(url))

        if audio_url:
            moderation_result = await self._moderation.moderate_audio(audio_url)
            results.append(ReviewResult(
                is_approved=moderation_result.is_safe,
                moderation_result=moderation_result,
            ))

        if not results:
            return ReviewResult(
                is_approved=True,
                moderation_result=ModerationResult(is_safe=True),
            )

        # Content is approved only if ALL parts are approved
        is_approved = all(r.is_approved for r in results)
        suggestions = []
        for r in results:
            suggestions.extend(r.suggestions)

        # Use the first moderation result as representative
        return ReviewResult(
            is_approved=is_approved,
            moderation_result=results[0].moderation_result,
            suggestions=suggestions,
        )
