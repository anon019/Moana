"""Planner Agent - 生成个性化周学习计划."""
from datetime import datetime, timedelta

from moana.agents.schemas import DayPlan, WeeklyPlan
from moana.services.llm import get_llm_service
from moana.themes import get_themes_for_age


class PlannerAgent:
    """周计划生成 Agent.

    根据孩子档案和已学内容，智能生成一周的学习计划。
    """

    def __init__(self):
        self._llm = get_llm_service()

    async def generate_weekly_plan(
        self,
        child_id: str,
        child_name: str,
        age_months: int,
        preferences: list[str] | None = None,
        learned_themes: list[str] | None = None,
    ) -> WeeklyPlan:
        """生成周学习计划.

        Args:
            child_id: 孩子 ID
            child_name: 孩子名字
            age_months: 月龄
            preferences: 偏好主题/角色
            learned_themes: 已学过的主题列表

        Returns:
            WeeklyPlan: 一周的学习计划
        """
        preferences = preferences or []
        learned_themes = learned_themes or []

        # 获取适合该年龄的主题
        available_themes = get_themes_for_age(age_months)
        theme_names = [t.name for t in available_themes]

        # 构建 prompt
        prompt = self._build_prompt(
            child_name=child_name,
            age_months=age_months,
            preferences=preferences,
            learned_themes=learned_themes,
            available_themes=theme_names,
        )

        # 调用 LLM
        result = await self._llm.generate_structured(
            prompt=prompt,
            output_schema=self._get_output_schema(),
            system_prompt=self._get_system_prompt(),
        )

        # 构建 WeeklyPlan
        week_start = self._get_next_monday()
        days = []
        for day_data in result["days"]:
            day_num = day_data["day"]
            day_date = week_start + timedelta(days=day_num - 1)
            days.append(DayPlan(
                day=day_num,
                date=day_date.strftime("%Y-%m-%d"),
                theme=day_data["theme"],
                category=day_data["category"],
                content_types=day_data["content_types"],
                story_hint=day_data["story_hint"],
                song_hint=day_data.get("song_hint"),
            ))

        return WeeklyPlan(
            week_start=week_start.strftime("%Y-%m-%d"),
            child_id=child_id,
            child_name=child_name,
            age_months=age_months,
            days=days,
        )

    def _build_prompt(
        self,
        child_name: str,
        age_months: int,
        preferences: list[str],
        learned_themes: list[str],
        available_themes: list[str],
    ) -> str:
        """构建 LLM prompt."""
        age_years = age_months // 12
        age_months_remainder = age_months % 12
        age_str = f"{age_years}岁{age_months_remainder}个月" if age_months_remainder else f"{age_years}岁"

        preferences_str = "、".join(preferences) if preferences else "无特别偏好"
        learned_str = "、".join(learned_themes) if learned_themes else "无"
        themes_str = "、".join(available_themes)

        return f"""请为{child_name}（{age_str}）制定一周的学习计划。

## 孩子信息
- 姓名：{child_name}
- 年龄：{age_str}（{age_months}个月）
- 偏好：{preferences_str}

## 已学主题（请避开，不要重复）
{learned_str}

## 可选主题
{themes_str}

## 要求
1. 生成7天的计划，每天1个主题
2. 习惯养成和认知世界主题交替或均衡分配
3. 根据孩子年龄选择合适难度的主题
4. 每天推荐合适的内容形式（picture_book/nursery_rhyme/video）
5. 为每个主题提供具体的创作提示（story_hint/song_hint）
6. 创作提示要融入孩子的名字和偏好

请生成计划："""

    def _get_system_prompt(self) -> str:
        """获取系统 prompt."""
        return """你是一位专业的早教规划师，负责为1-3岁幼儿制定个性化的学习计划。

你的规划原则：
1. 循序渐进：从简单到复杂
2. 寓教于乐：内容要有趣味性
3. 个性化：融入孩子的名字和喜好
4. 均衡发展：习惯养成和认知世界并重
5. 避免重复：不安排最近学过的主题

输出要求：
- 每天的 content_types 从 ["picture_book", "nursery_rhyme", "video"] 中选择
- story_hint 要具体，包含故事情节方向
- song_hint 要描述音乐风格和歌词主题"""

    def _get_output_schema(self) -> dict:
        """获取输出 schema."""
        return {
            "type": "object",
            "properties": {
                "days": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day": {"type": "integer", "minimum": 1, "maximum": 7},
                            "theme": {"type": "string"},
                            "category": {"type": "string", "enum": ["habit", "cognition"]},
                            "content_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["picture_book", "nursery_rhyme", "video"]}
                            },
                            "story_hint": {"type": "string"},
                            "song_hint": {"type": "string"},
                        },
                        "required": ["day", "theme", "category", "content_types", "story_hint"]
                    }
                }
            },
            "required": ["days"]
        }

    def _get_next_monday(self) -> datetime:
        """获取下一个周一的日期."""
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # 如果今天是周一，返回下周一
        return today + timedelta(days=days_until_monday)
