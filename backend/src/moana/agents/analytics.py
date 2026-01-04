# src/moana/agents/analytics.py
from dataclasses import dataclass
from typing import Optional

from moana.services.llm.gemini import GeminiService
from moana.services.analytics import ChildStats


@dataclass
class AnalyticsInsight:
    """AI-generated insight from analytics."""
    summary: str
    recommendations: list[str]
    highlights: list[str]
    concerns: list[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "recommendations": self.recommendations,
            "highlights": self.highlights,
            "concerns": self.concerns,
        }


ANALYTICS_SYSTEM_PROMPT = """你是一位专业的早期教育顾问，根据孩子的学习数据提供个性化建议。

分析原则：
1. 正向鼓励：强调孩子的进步和成就
2. 平衡发展：关注多方面能力培养
3. 适龄建议：考虑孩子的年龄特点
4. 家长友好：使用通俗易懂的语言

输出要求：
- 简洁明了，重点突出
- 建议具体可行
- 语气温暖友好"""


class AnalyticsAgent:
    """Agent for generating AI insights from analytics."""

    def __init__(self):
        self._llm = GeminiService()

    async def generate_insights(
        self,
        stats: ChildStats,
        child_name: str,
        age_months: int,
    ) -> AnalyticsInsight:
        """Generate AI insights from child statistics.

        Args:
            stats: Child statistics
            child_name: Name of the child
            age_months: Age in months

        Returns:
            AnalyticsInsight with AI-generated content
        """
        # Format statistics for the prompt
        stats_summary = self._format_stats(stats)

        prompt = f"""请分析以下{age_months}个月大的孩子"{child_name}"的学习数据，并提供建议：

{stats_summary}

请输出JSON格式：
{{
  "summary": "简短的总体评价（50字以内）",
  "highlights": ["亮点1", "亮点2"],
  "recommendations": ["建议1", "建议2", "建议3"],
  "concerns": ["需要关注的点"]
}}"""

        try:
            response = await self._llm.generate(
                prompt=prompt,
                system_prompt=ANALYTICS_SYSTEM_PROMPT,
                temperature=0.5,
            )

            # Parse JSON response
            import json
            data = json.loads(response)

            return AnalyticsInsight(
                summary=data.get("summary", "学习进度良好"),
                recommendations=data.get("recommendations", []),
                highlights=data.get("highlights", []),
                concerns=data.get("concerns", []),
            )
        except (json.JSONDecodeError, Exception):
            # Return default insight if AI fails
            return self._generate_default_insight(stats, child_name)

    def _format_stats(self, stats: ChildStats) -> str:
        """Format statistics for prompt."""
        lines = [
            f"- 总播放次数: {stats.total_plays}",
            f"- 总学习时长: {stats.total_duration // 60}分钟",
            f"- 连续学习天数: {stats.streak_days}天",
        ]

        if stats.favorite_content_type:
            type_names = {
                "picture_book": "绘本",
                "nursery_rhyme": "儿歌",
                "video": "视频",
            }
            lines.append(f"- 最喜欢的内容类型: {type_names.get(stats.favorite_content_type.value, stats.favorite_content_type.value)}")

        if stats.content_stats:
            lines.append("\n内容类型分布:")
            for cs in stats.content_stats:
                type_name = {
                    "picture_book": "绘本",
                    "nursery_rhyme": "儿歌",
                    "video": "视频",
                }.get(cs.content_type.value, cs.content_type.value)
                lines.append(f"  - {type_name}: {cs.total_plays}次播放, {cs.unique_contents}个内容")

        return "\n".join(lines)

    def _generate_default_insight(
        self,
        stats: ChildStats,
        child_name: str,
    ) -> AnalyticsInsight:
        """Generate default insight when AI is unavailable."""
        summary = f"{child_name}的学习表现良好"
        highlights = []
        recommendations = []
        concerns = []

        if stats.streak_days >= 3:
            highlights.append(f"连续{stats.streak_days}天坚持学习，习惯养成中")

        if stats.total_plays >= 10:
            highlights.append("学习积极性高，内容丰富")

        if len(stats.content_stats) == 1:
            recommendations.append("可以尝试更多类型的内容，促进全面发展")

        if stats.total_duration < 300:  # Less than 5 minutes
            recommendations.append("适当增加每日学习时间")
        elif stats.total_duration > 1800:  # More than 30 minutes
            concerns.append("注意控制屏幕使用时间")

        if not highlights:
            highlights.append("开始学习之旅")
        if not recommendations:
            recommendations.append("保持当前的学习节奏")

        return AnalyticsInsight(
            summary=summary,
            recommendations=recommendations,
            highlights=highlights,
            concerns=concerns,
        )
