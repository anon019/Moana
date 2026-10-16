from dataclasses import dataclass, field
from typing import Optional

from moana.services.llm import get_llm_service
from moana.agents.schemas import PictureBookOutline


# ========== 增强配置数据类 ==========

@dataclass
class StoryEnhancement:
    """故事增强配置（全部可选，由配置的文本模型智能推断）."""
    narrative_pace: str | None = None      # relaxed/lively/progressive
    interaction_density: str | None = None  # minimal/moderate/intensive
    educational_focus: str | None = None    # cognitive/behavioral/emotional/imaginative
    language_style: str | None = None       # simple/rhythmic/onomatopoeia/repetitive
    plot_complexity: str | None = None      # linear/twist/ensemble
    ending_style: str | None = None         # warm/open/summary


@dataclass
class VisualEnhancement:
    """视觉增强配置（全部可选，由配置的文本模型智能推断）."""
    time_atmosphere: str | None = None      # morning/afternoon/sunset/night/dreamy
    scene_environment: str | None = None    # indoor/garden/forest/beach/clouds
    emotional_tone: str | None = None       # cheerful/cozy/playful/peaceful/curious
    composition_style: str | None = None    # close_up/panorama/interaction/narrative
    lighting_effect: str | None = None      # soft_natural/warm_sunlight/dreamy_glow/cozy_lamp


# ========== 风格配置 ==========

@dataclass
class StyleConfig:
    """绘本风格配置."""
    art_style: str = "pixar_3d"
    protagonist_animal: str = "bunny"
    protagonist_color: str = "white"  # 实际默认色由 pipeline 层按动物类型决定
    protagonist_accessory: str | None = None
    color_palette: str = "pastel"
    # 新增：增强配置
    story_enhancement: StoryEnhancement | None = None
    visual_enhancement: VisualEnhancement | None = None


# 美术风格示例（仅用于帮助大模型理解，不作为限制）
# 实际风格由大模型根据 art_style 参数自行理解和生成
ART_STYLE_EXAMPLES = {
    "pixar_3d": "Pixar-style 3D rendered, soft ambient lighting, rounded shapes",
    "chibi": "Chibi style, super deformed, cute big head small body, kawaii",
    "ghibli": "Studio Ghibli style, hand-drawn animation, soft colors, magical",
    "watercolor": "Soft watercolor painting, hand-painted texture, gentle brushstrokes",
}

# 主角动物映射表
PROTAGONIST_PROMPTS = {
    "bunny": "bunny character with long upright ears with pink inner ears, round head, big sparkling eyes, small button nose, short fluffy tail, soft chubby body",
    "bear": "bear cub character with round ears on top of head, small beady eyes, wide snout with a little nose, chubby round body, short stubby limbs, friendly smile",
    "cat": "cat character with pointy triangle ears, large bright eyes with slit pupils, long whiskers, small pink nose, slender body, long swaying tail",
    "dog": "puppy character with big floppy droopy ears, large round puppy eyes, wet black nose, wagging short tail, soft chubby body, tongue slightly out",
    "panda": "panda character with round ears, iconic black eye patches, black and white fur pattern, round plump body, short limbs, gentle calm expression",
    "fox": "fox character with large pointy ears with dark tips, narrow bright eyes, long pointed snout, big fluffy tail with a white tip, slender agile body",
    "elephant": "baby elephant character with very big floppy ears, tiny kind eyes, long curving trunk, round stout body, thick sturdy legs, small thin tail",
    "monkey": "monkey character with round face, big curious eyes, wide grin, small round ears on sides of head, long curly tail, lean agile body, expressive eyebrows",
    "penguin": "penguin character with round belly, black and white tuxedo-like body, small flipper wings, short orange beak, tiny dot eyes, waddling upright posture",
}

# 配饰映射表
ACCESSORY_PROMPTS = {
    "blue overalls": "wearing blue overalls",
    "red scarf": "wearing a red scarf",
    "yellow raincoat": "wearing a yellow raincoat",
    "pink dress": "wearing a pink dress",
    "green vest": "wearing a green vest",
    "purple hat": "wearing a purple hat",
    "orange backpack": "carrying an orange backpack",
    "yellow scarf": "wearing a yellow scarf",
    "red bow": "with a red bow",
    "blue collar": "wearing a blue collar",
    "bamboo": "holding bamboo",
}

# 色彩风格映射表
COLOR_PALETTE_PROMPTS = {
    "pastel": "pastel color palette, soft and gentle tones",
    "vibrant": "vibrant saturated colors, energetic and lively",
    "warm": "warm color palette, cozy golden and orange tones",
    "cool": "cool color palette, calming blues and greens",
    "monochrome": "limited color palette, elegant and simple",
}

# 配角设定（固定）
SUPPORTING_CHARACTERS = {
    "小猫": "a cute orange tabby cat character with pointy ears, large bright eyes, long whiskers, a red bow on head",
    "小狗": "a cute brown puppy character with big floppy droopy ears, round puppy eyes, wet black nose, wagging tail",
    "小熊": "a cute brown bear cub character with round ears, small beady eyes, chubby body, wearing a yellow scarf",
    "小兔子": "a cute white bunny character with long upright ears with pink inner ears, big sparkling eyes, fluffy tail",
    "小熊猫": "a cute panda character with round ears, black eye patches, black and white fur, round plump body",
    "小狐狸": "a cute orange fox character with large pointy ears, narrow bright eyes, big fluffy tail with white tip",
}


def build_protagonist_desc(style: StyleConfig) -> str:
    """根据风格配置构建主角描述.

    此函数是主角描述的唯一构建入口，被系统提示词和管线层共同使用，
    确保两处的角色描述始终一致。
    """
    animal_desc = PROTAGONIST_PROMPTS.get(style.protagonist_animal, PROTAGONIST_PROMPTS["bunny"])
    desc = f"a cute {style.protagonist_color} {animal_desc}"
    if style.protagonist_accessory:
        accessory_desc = ACCESSORY_PROMPTS.get(style.protagonist_accessory)
        if accessory_desc:
            desc += f", {accessory_desc}"
    return desc


def build_system_prompt(style: StyleConfig) -> str:
    """根据风格配置动态构建系统提示词.

    关键设计：不预设有限的风格列表，而是将 art_style 参数直接告诉大模型，
    让大模型根据风格名称自行理解并生成合适的 image_prompt。
    这样即使前端添加新的风格，后端也无需修改。
    """

    # 构建主角描述
    protagonist_desc = build_protagonist_desc(style)

    # 获取色彩风格
    color_desc = COLOR_PALETTE_PROMPTS.get(style.color_palette, COLOR_PALETTE_PROMPTS["pastel"])

    # === 构建故事增强描述 ===
    story_hints = []
    if style.story_enhancement:
        se = style.story_enhancement
        if se.narrative_pace:
            story_hints.append(f"叙事节奏：{se.narrative_pace}")
        if se.interaction_density:
            story_hints.append(f"互动密度：{se.interaction_density}")
        if se.educational_focus:
            story_hints.append(f"教育侧重：{se.educational_focus}")
        if se.language_style:
            story_hints.append(f"语言风格：{se.language_style}")
        if se.plot_complexity:
            story_hints.append(f"情节复杂度：{se.plot_complexity}")
        if se.ending_style:
            story_hints.append(f"结局风格：{se.ending_style}")

    story_enhancement_text = "\n".join(f"  - {h}" for h in story_hints) if story_hints else "  （由你根据主题和孩子年龄智能推断）"

    # === 构建视觉增强描述 ===
    visual_hints = []
    if style.visual_enhancement:
        ve = style.visual_enhancement
        if ve.time_atmosphere:
            visual_hints.append(f"时间氛围：{ve.time_atmosphere}")
        if ve.scene_environment:
            visual_hints.append(f"场景环境：{ve.scene_environment}")
        if ve.emotional_tone:
            visual_hints.append(f"情感基调：{ve.emotional_tone}")
        if ve.composition_style:
            visual_hints.append(f"画面构图：{ve.composition_style}")
        if ve.lighting_effect:
            visual_hints.append(f"光照效果：{ve.lighting_effect}")

    visual_enhancement_text = "\n".join(f"  - {h}" for h in visual_hints) if visual_hints else "  （由你根据故事情节智能推断）"

    # 风格示例（帮助大模型理解常见风格的表达方式）
    style_examples = """
    - pixar_3d: "Pixar-style 3D rendered illustration, soft ambient lighting, rounded shapes"
    - chibi: "Chibi style illustration, super deformed, cute big head small body, kawaii aesthetic"
    - ghibli: "Studio Ghibli style, hand-drawn animation look, soft colors, magical atmosphere"
    - watercolor: "Soft watercolor painting, hand-painted texture, gentle brushstrokes"
    - anime: "Anime style illustration, big expressive eyes, Japanese kawaii"
    """

    return f"""你是一位专业的儿童绘本作家，专门为1-3岁幼儿创作启蒙故事。

创作原则：
1. 语言简单：每页1-2句话，使用幼儿能理解的词汇
2. 重复性强：关键词语重复出现，帮助记忆
3. 节奏感好：适合朗读，有韵律感
4. 正向引导：传递积极的价值观和行为习惯
5. 互动设计：每2-3页设置一个简单的互动问题

故事结构：
- 开头：引入场景和主角
- 中间：通过有趣的情节展开主题
- 结尾：正向的结局和简单的总结

互动类型：
- tap_count: 数数（数一数有几个...）
- choice: 选择（应该选哪个...）
- tap_object: 指认（找一找哪个是...）

【重要】图像提示词规则：

1. 美术风格（用户选择）："{style.art_style}"
   - 你需要根据这个风格名称，生成符合该风格的英文图像描述
   - 每页的 image_prompt 都必须体现这个风格
   - 常见风格示例：{style_examples}
   - 如果是你不熟悉的风格名称，请根据名称含义合理推断并生成对应的风格描述

2. 色彩风格：{color_desc}
   - 每页图像都应该符合这个色彩基调

3. 【角色一致性 - 最重要的规则】：
   - 主角固定描述（以下称为 PROTAGONIST_TAG）: "{protagonist_desc}"
   - ⚠️ 每一页的 image_prompt 都必须【逐字复制】上面的 PROTAGONIST_TAG，不可省略、改写或简化
   - 不要用代词（如 "the bunny", "it"）替代完整描述，每页都要写完整的角色描述
   - 如果主角与某个物品互动（如抱着大苹果），主角描述必须在前，动作和物品在后
   - 主角在画面中必须是视觉焦点，占画面显著位置，不能被遮挡或缩小到看不清

4. 【道具/物品一致性】：
   - 如果故事中有一个核心道具或物品（如"大苹果"、"红气球"），请在第一页定义它的英文描述（大小、颜色、形状）
   - 之后每一页该物品出现时，必须使用【完全相同的英文描述】
   - 物品的大小比例要保持一致：如果第一页苹果比主角还大，后面每页都要保持这个比例
   - 不要在某些页面突然替换或省略核心道具

5. 配角设定：
   - 小猫: "a cute orange tabby cat character with a red bow"
   - 小狗: "a cute brown puppy character with floppy ears"
   - 小熊: "a cute brown bear cub character with a yellow scarf"
   - 配角出现时也要使用完整描述，不要简化

6. 禁止事项：
   - 不要使用 boy、girl、child、toddler、kid 等人类词汇
   - 不要使用人名
   - 不要在图片中包含任何文字（添加 "no text or letters in image"）
   - 不要在不同页面改变主角的外观特征（颜色、配饰、体型）
   - 不要引入提示词中未定义的新角色或物品来替代主角

【故事创作增强指引】
用户希望的故事风格：
{story_enhancement_text}

请根据以上指引调整故事的节奏、语言、互动设计和情节安排。

【图像提示词增强指引】
用户希望的视觉风格：
{visual_enhancement_text}

请在生成每页的 image_prompt 时，将以上视觉元素自然融入。例如：
- morning → "soft morning light, golden sunrise, fresh atmosphere"
- cheerful → "bright colors, happy expressions, dynamic poses"
- close_up → "character close-up shot, detailed expressions"

7. image_prompt 格式要求（严格遵守此结构）：
   - 必须是英文
   - 格式：[风格描述], [PROTAGONIST_TAG 逐字复制], [动作和表情], [核心道具完整描述], [场景背景], {color_desc}, child-friendly, no text or letters in image
   - 每页的 PROTAGONIST_TAG 部分必须与第3条中的描述完全一致，一个词都不能少

8. 示例（风格为 chibi 时，主角与大苹果互动的故事）：
   第1页: "Chibi style illustration, super deformed, {protagonist_desc}, standing next to a giant shiny red apple twice the size of the character, looking up with amazed expression, sunny garden background, kawaii aesthetic, {color_desc}, child-friendly, no text or letters in image"
   第2页: "Chibi style illustration, super deformed, {protagonist_desc}, hugging a giant shiny red apple twice the size of the character, happy laughing expression, sunny garden background, kawaii aesthetic, {color_desc}, child-friendly, no text or letters in image"
   注意：两页中主角描述和苹果描述完全一致，只有动作和表情不同。

图像提示词必须是英文！"""


# 默认系统提示词（向后兼容）
STORY_SYSTEM_PROMPT = build_system_prompt(StyleConfig())


class StoryAgent:
    """Agent for generating picture book stories."""

    def __init__(self):
        self._llm = get_llm_service()

    async def generate_outline(
        self,
        child_name: str,
        age_months: int,
        theme_topic: str,
        theme_category: str,
        favorite_characters: list[str] | None = None,
        num_pages: int = 8,
        style_config: StyleConfig | None = None,
    ) -> PictureBookOutline:
        """Generate a picture book outline.

        Args:
            child_name: 孩子名字
            age_months: 孩子月龄
            theme_topic: 主题（如"刷牙"）
            theme_category: 类别（habit/cognition）
            favorite_characters: 喜欢的角色列表
            num_pages: 绘本页数
            style_config: 风格配置（美术风格、主角、色彩）
        """
        chars = favorite_characters or ["小兔子"]
        chars_str = "、".join(chars)

        # 使用风格配置动态生成 system prompt
        if style_config:
            system_prompt = build_system_prompt(style_config)
        else:
            system_prompt = STORY_SYSTEM_PROMPT

        prompt = f"""请为{age_months}个月大的孩子"{child_name}"创作一个关于「{theme_topic}」的绘本故事。

要求：
- 故事主角是{child_name}，配角可以是{chars_str}
- 共{num_pages}页，每页1-2句简短的话
- 主题类别：{"习惯养成" if theme_category == "habit" else "认知世界"}
- 设置2-3个简单的互动问题
- 为每页提供详细的英文插图提示词（用于AI生图）

请输出完整的绘本结构。"""

        outline = await self._llm.generate_structured(
            prompt=prompt,
            output_schema=PictureBookOutline,
            system_prompt=system_prompt,
            temperature=0.8,
        )

        return outline

    async def refine_page(
        self,
        page: dict,
        feedback: str,
    ) -> dict:
        """Refine a single page based on feedback."""
        prompt = f"""请根据以下反馈修改绘本页面：

当前页面：
{page}

反馈：{feedback}

请输出修改后的页面。"""

        response = await self._llm.generate(
            prompt=prompt,
            system_prompt=STORY_SYSTEM_PROMPT,
            temperature=0.7,
        )

        return {"refined": response}
