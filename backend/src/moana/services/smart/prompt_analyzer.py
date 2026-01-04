"""Smart prompt analyzer for user custom descriptions."""
import json
import logging
from dataclasses import dataclass

from google import genai
from google.genai import types

from moana.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of analyzing user's custom prompt."""
    theme_category: str      # AI inferred category
    theme_topic: str         # Extracted topic
    enhanced_prompt: str     # Enhanced prompt for generation
    educational_goal: str    # Educational objective
    title: str               # Suggested title


class SmartPromptAnalyzer:
    """Analyze user custom descriptions and extract structured data."""

    ANALYSIS_PROMPT = """你是一个儿童教育内容分析专家。分析用户的描述，提取以下信息：

用户描述: {custom_prompt}
宝贝名字: {child_name}
宝贝年龄: {age_months}个月
内容类型: {content_type}

请分析并返回 JSON 格式：
{{
    "theme_category": "分类（选择最合适的一个英文单词）: habit(习惯养成), cognition(认知学习), emotion(情感发展), social(社交能力), creativity(创造力), safety(安全教育), language(语言发展), motor(运动发展), music(音乐艺术), nature(自然探索), family(家庭亲情), friendship(友谊交往), other(其他)",
    "theme_topic": "主题关键词（2-4个字，如: 吃蔬菜、刷牙、分享）",
    "enhanced_prompt": "增强后的创作提示（50-100字，适合{content_type}创作，融入宝贝名字{child_name}）",
    "educational_goal": "教育目标（一句话描述）",
    "title": "建议的标题（包含宝贝名字，如: {child_name}的蔬菜大冒险）"
}}

只返回 JSON，不要其他内容。theme_category 只填写英文单词，不要填写中文。"""

    def __init__(self):
        settings = get_settings()
        self._client = genai.Client(api_key=settings.google_api_key)
        self._model = "gemini-3-flash-preview"

    async def analyze(
        self,
        custom_prompt: str,
        child_name: str,
        age_months: int,
        content_type: str,
    ) -> AnalysisResult:
        """Analyze user's custom prompt and return structured result.

        Args:
            custom_prompt: User's description (max 500 chars)
            child_name: Child's name for personalization
            age_months: Child's age in months
            content_type: "picture_book" | "nursery_rhyme" | "video"

        Returns:
            AnalysisResult with extracted theme and enhanced prompt
        """
        prompt = self.ANALYSIS_PROMPT.format(
            custom_prompt=custom_prompt,
            child_name=child_name,
            age_months=age_months,
            content_type=content_type,
        )

        logger.info(f"Analyzing prompt: {custom_prompt[:50]}...")

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            result_text = response.text.strip()
            logger.debug(f"Analysis result: {result_text}")

            data = json.loads(result_text)

            return AnalysisResult(
                theme_category=data.get("theme_category", "other"),
                theme_topic=data.get("theme_topic", custom_prompt[:20]),
                enhanced_prompt=data.get("enhanced_prompt", custom_prompt),
                educational_goal=data.get("educational_goal", ""),
                title=data.get("title", f"{child_name}的故事"),
            )

        except Exception as e:
            logger.warning(f"Prompt analysis failed: {e}, using defaults", exc_info=True)
            # Fallback to defaults
            return AnalysisResult(
                theme_category="other",
                theme_topic=custom_prompt[:20],
                enhanced_prompt=custom_prompt,
                educational_goal="",
                title=f"{child_name}的故事",
            )
