"""Intent Agent - 理解家长自然语言输入."""
from moana.agents.schemas import ParsedIntent
from moana.services.llm import get_llm_service


class IntentAgent:
    """意图理解 Agent.

    解析家长的自然语言输入，提取主题并生成定制化创作提示。
    """

    def __init__(self):
        self._llm = get_llm_service()

    async def parse(
        self,
        child_name: str,
        age_months: int,
        user_input: str,
        preferred_types: list[str] | None = None,
    ) -> ParsedIntent:
        """解析家长输入.

        Args:
            child_name: 孩子名字
            age_months: 月龄
            user_input: 家长的自然语言输入
            preferred_types: 希望生成的内容类型

        Returns:
            ParsedIntent: 解析后的意图
        """
        preferred_types = preferred_types or []

        prompt = self._build_prompt(
            child_name=child_name,
            age_months=age_months,
            user_input=user_input,
            preferred_types=preferred_types,
        )

        result = await self._llm.generate_structured(
            prompt=prompt,
            output_schema=self._get_output_schema(),
            system_prompt=self._get_system_prompt(),
        )

        return ParsedIntent(
            intent_type=result["intent_type"],
            original_input=user_input,
            theme=result["theme"],
            category=result["category"],
            educational_goal=result["educational_goal"],
            story_prompt=result["story_prompt"],
            song_prompt=result.get("song_prompt"),
            video_prompt=result.get("video_prompt"),
            recommended_types=result["recommended_types"],
        )

    def _build_prompt(
        self,
        child_name: str,
        age_months: int,
        user_input: str,
        preferred_types: list[str],
    ) -> str:
        """构建 LLM prompt."""
        age_years = age_months // 12
        age_months_remainder = age_months % 12
        age_str = f"{age_years}岁{age_months_remainder}个月" if age_months_remainder else f"{age_years}岁"

        types_str = "、".join(preferred_types) if preferred_types else "由你推荐"

        return f"""请理解以下家长输入，并生成适合幼儿的内容创作提示。

## 孩子信息
- 姓名：{child_name}
- 年龄：{age_str}（{age_months}个月）

## 家长输入
"{user_input}"

## 希望的内容形式
{types_str}

## 任务
1. 判断输入类型（ip/life_event/interest/behavior）
2. 提取或转化为适合幼儿的主题
3. 确定主题分类（habit/cognition）
4. 设定教育目标
5. 生成针对性的创作提示（绘本/儿歌/视频）
6. 推荐合适的内容形式

请分析并生成："""

    def _get_system_prompt(self) -> str:
        """获取系统 prompt."""
        return """你是一位专业的早教内容策划师，擅长理解家长需求并转化为适合1-3岁幼儿的教育内容。

输入类型说明：
- ip: 影视/动画IP，如"疯狂动物城"、"小猪佩奇"
- life_event: 生活事件，如"要打疫苗"、"第一次坐飞机"
- interest: 兴趣爱好，如"喜欢恐龙"、"爱挖掘机"
- behavior: 行为引导，如"不想刷牙"、"怕黑"

创作提示要求：
1. story_prompt: 具体的故事情节方向，融入孩子名字，适合年龄
2. song_prompt: 描述音乐风格和歌词主题，朗朗上口
3. video_prompt: 如果适合，描述动画风格和内容

注意：
- 所有内容必须适合幼儿
- 行为引导类要正面积极，不要说教
- IP类可以借鉴风格但要原创内容"""

    def _get_output_schema(self) -> dict:
        """获取输出 schema."""
        return {
            "type": "object",
            "properties": {
                "intent_type": {
                    "type": "string",
                    "enum": ["ip", "life_event", "interest", "behavior"]
                },
                "theme": {"type": "string"},
                "category": {
                    "type": "string",
                    "enum": ["habit", "cognition"]
                },
                "educational_goal": {"type": "string"},
                "story_prompt": {"type": "string"},
                "song_prompt": {"type": "string"},
                "video_prompt": {"type": "string"},
                "recommended_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["picture_book", "nursery_rhyme", "video"]
                    }
                },
            },
            "required": [
                "intent_type", "theme", "category",
                "educational_goal", "story_prompt", "recommended_types"
            ]
        }
