# src/moana/styles/__init__.py
"""统一的风格配置模块.

为绘本、儿歌、视频提供统一的风格参数管理。
"""
from dataclasses import dataclass, field
from typing import Optional


# ========== 风格配置数据类 ==========

@dataclass
class ProtagonistStyle:
    """主角风格配置."""
    animal: str = "bunny"
    color: str = "white"
    accessory: str = "blue overalls"


@dataclass
class VisualStyle:
    """视觉风格配置（用于绘本和封面）."""
    art_style: str = "pixar_3d"
    protagonist: ProtagonistStyle = field(default_factory=ProtagonistStyle)
    color_palette: str = "pastel"


@dataclass
class MusicStyleConfig:
    """音乐风格配置."""
    mood: str = "cheerful"  # cheerful, gentle, playful, lullaby, educational
    tempo: str = "medium"   # slow, medium, fast
    instruments: str = "children"  # children, acoustic, electronic, orchestral


# ========== 美术风格映射 ==========

ART_STYLE_PROMPTS = {
    "pixar_3d": {
        "prefix": "Pixar-style 3D rendered illustration,",
        "suffix": "soft ambient lighting, rounded shapes, high quality render",
        "name": "皮克斯3D",
        "name_en": "Pixar 3D",
    },
    "watercolor": {
        "prefix": "Soft watercolor painting illustration, hand-painted texture,",
        "suffix": "gentle brushstrokes, artistic watercolor effects, soft edges",
        "name": "水彩手绘",
        "name_en": "Watercolor",
    },
    "flat_vector": {
        "prefix": "Modern flat vector illustration, clean lines, geometric shapes,",
        "suffix": "minimalist design, bold colors, crisp edges",
        "name": "扁平插画",
        "name_en": "Flat Vector",
    },
    "crayon": {
        "prefix": "Children's crayon drawing style, colorful and playful,",
        "suffix": "hand-drawn texture, childlike charm, warm feeling",
        "name": "蜡笔涂鸦",
        "name_en": "Crayon",
    },
    "anime": {
        "prefix": "Cute anime style illustration, big expressive eyes, Japanese kawaii,",
        "suffix": "soft shading, adorable character design, vibrant colors",
        "name": "日系动漫",
        "name_en": "Anime",
    },
}

# ========== 主角动物映射 ==========

PROTAGONIST_ANIMALS = {
    "bunny": {
        "name": "小兔子",
        "prompt": "bunny character with pink inner ears",
        "default_color": "white",
        "default_accessory": "blue overalls",
    },
    "bear": {
        "name": "小熊",
        "prompt": "bear cub character",
        "default_color": "brown",
        "default_accessory": "yellow scarf",
    },
    "cat": {
        "name": "小猫",
        "prompt": "cat character with whiskers",
        "default_color": "orange tabby",
        "default_accessory": "red bow",
    },
    "dog": {
        "name": "小狗",
        "prompt": "puppy character with floppy ears",
        "default_color": "golden",
        "default_accessory": "blue collar",
    },
    "panda": {
        "name": "小熊猫",
        "prompt": "panda character with round ears",
        "default_color": "black and white",
        "default_accessory": "bamboo",
    },
    "fox": {
        "name": "小狐狸",
        "prompt": "fox character with a fluffy tail",
        "default_color": "orange",
        "default_accessory": "green vest",
    },
}

# ========== 配饰映射 ==========

ACCESSORIES = {
    "blue overalls": {"name": "蓝色背带裤", "prompt": "wearing blue overalls"},
    "red scarf": {"name": "红色围巾", "prompt": "wearing a red scarf"},
    "yellow scarf": {"name": "黄色围巾", "prompt": "wearing a yellow scarf"},
    "yellow raincoat": {"name": "黄色雨衣", "prompt": "wearing a yellow raincoat"},
    "pink dress": {"name": "粉色连衣裙", "prompt": "wearing a pink dress"},
    "green vest": {"name": "绿色小马甲", "prompt": "wearing a green vest"},
    "purple hat": {"name": "紫色帽子", "prompt": "wearing a purple hat"},
    "orange backpack": {"name": "橙色小书包", "prompt": "carrying an orange backpack"},
    "red bow": {"name": "红色蝴蝶结", "prompt": "with a red bow"},
    "blue collar": {"name": "蓝色项圈", "prompt": "wearing a blue collar"},
    "bamboo": {"name": "竹子", "prompt": "holding bamboo"},
}

# ========== 色彩风格映射 ==========

COLOR_PALETTES = {
    "pastel": {
        "name": "马卡龙色",
        "description": "柔和温馨",
        "prompt": "pastel color palette, soft and gentle tones",
        "colors": ["#FFB5BA", "#B5D8FF", "#C5F0A4", "#FFF5BA"],
    },
    "vibrant": {
        "name": "活力鲜艳",
        "description": "明快活泼",
        "prompt": "vibrant saturated colors, energetic and lively",
        "colors": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3"],
    },
    "warm": {
        "name": "暖暖阳光",
        "description": "温暖舒适",
        "prompt": "warm color palette, cozy golden and orange tones",
        "colors": ["#FFBE76", "#FF7979", "#F8B739", "#FFD93D"],
    },
    "cool": {
        "name": "清新冷调",
        "description": "清爽宁静",
        "prompt": "cool color palette, calming blues and greens",
        "colors": ["#74B9FF", "#81ECEC", "#A29BFE", "#DFE6E9"],
    },
    "monochrome": {
        "name": "简约单色",
        "description": "优雅简洁",
        "prompt": "limited color palette, elegant and simple",
        "colors": ["#2D3436", "#636E72", "#B2BEC3", "#DFE6E9"],
    },
}

# ========== 音乐风格映射 ==========

MUSIC_MOODS = {
    "cheerful": {
        "name": "欢快活泼",
        "description": "适合日常活动主题",
        "prompt": "cheerful, upbeat, happy, bouncy rhythm",
        "suno_tags": "children's song, cheerful, upbeat, happy",
    },
    "gentle": {
        "name": "温柔舒缓",
        "description": "适合睡前或安静时刻",
        "prompt": "gentle, soft, soothing, calm",
        "suno_tags": "children's lullaby, gentle, soft, soothing",
    },
    "playful": {
        "name": "调皮有趣",
        "description": "适合游戏互动主题",
        "prompt": "playful, fun, energetic, silly",
        "suno_tags": "children's song, playful, fun, energetic",
    },
    "lullaby": {
        "name": "摇篮曲",
        "description": "适合哄睡",
        "prompt": "lullaby, peaceful, dreamy, slow tempo",
        "suno_tags": "lullaby, peaceful, dreamy, slow",
    },
    "educational": {
        "name": "教育启蒙",
        "description": "适合认知学习主题",
        "prompt": "educational, clear vocals, moderate tempo",
        "suno_tags": "children's educational song, clear vocals, moderate tempo",
    },
}

# ========== 视频动效风格映射 ==========

VIDEO_MOTION_STYLES = {
    "gentle": {
        "name": "轻柔缓动",
        "description": "适合睡前故事",
        "prompt": "gentle camera movement, slow pan, soft transition",
    },
    "dynamic": {
        "name": "活泼动感",
        "description": "适合活动主题",
        "prompt": "dynamic camera movement, zoom in/out, lively motion",
    },
    "static": {
        "name": "静态展示",
        "description": "专注画面内容",
        "prompt": "static shot, minimal movement, focus on illustration",
    },
}


# ========== 辅助函数 ==========

def build_protagonist_prompt(style: ProtagonistStyle) -> str:
    """构建主角的图像提示词."""
    animal_info = PROTAGONIST_ANIMALS.get(style.animal, PROTAGONIST_ANIMALS["bunny"])
    accessory_info = ACCESSORIES.get(style.accessory, ACCESSORIES["blue overalls"])

    return f"a cute {style.color} {animal_info['prompt']}, {accessory_info['prompt']}"


def build_art_style_prompt(art_style: str, color_palette: str) -> tuple[str, str]:
    """构建美术风格的前缀和后缀提示词.

    Returns:
        (prefix, suffix) 提示词元组
    """
    art = ART_STYLE_PROMPTS.get(art_style, ART_STYLE_PROMPTS["pixar_3d"])
    palette = COLOR_PALETTES.get(color_palette, COLOR_PALETTES["pastel"])

    prefix = art["prefix"]
    suffix = f"{art['suffix']}, {palette['prompt']}, no text or letters in image"

    return prefix, suffix


def build_cover_prompt(
    theme_topic: str,
    child_name: str,
    visual_style: Optional[VisualStyle] = None,
    favorite_characters: Optional[list[str]] = None,
) -> str:
    """构建封面图提示词（用于儿歌封面）."""
    style = visual_style or VisualStyle()

    # 获取美术风格
    art_prefix, art_suffix = build_art_style_prompt(style.art_style, style.color_palette)

    # 构建主角描述
    protagonist_desc = build_protagonist_prompt(style.protagonist)

    # 配角描述
    chars = favorite_characters or []
    chars_str = ", ".join(chars[:2]) if chars else "a friendly companion character"

    return f"""{art_prefix} A cute storybook illustration for a children's song about "{theme_topic}".

Main character: {protagonist_desc} (representing {child_name})
Supporting characters: {chars_str}
Scene: Cheerful, colorful, engaging activity related to {theme_topic}
Mood: Happy, encouraging, fun

{art_suffix}

IMPORTANT: Do NOT include any text, letters, words, numbers, or written characters in the image. Pure illustration only."""


def get_style_options() -> dict:
    """获取所有可用的风格选项（供 API 返回给前端）."""
    # 导入 TTS 音色选项和视频选项
    from moana.services.tts.qwen import QwenTTSService
    from moana.services.video.wanx import WanxVideoService

    return {
        "art_styles": [
            {
                "id": key,
                "name": val["name"],
                "name_en": val["name_en"],
                "description": f"使用{val['name']}风格绘制",
                "preview_url": f"https://example.com/static/styles/{key}.jpg",
                "recommended": key == "pixar_3d",
            }
            for key, val in ART_STYLE_PROMPTS.items()
        ],
        "protagonists": [
            {
                "animal": key,
                "name": val["name"],
                "default_color": val["default_color"],
                "default_accessory": val["default_accessory"],
                "preview_url": f"https://example.com/static/characters/{key}.jpg",
            }
            for key, val in PROTAGONIST_ANIMALS.items()
        ],
        "color_palettes": [
            {
                "id": key,
                "name": val["name"],
                "description": val["description"],
                "colors": val["colors"],
            }
            for key, val in COLOR_PALETTES.items()
        ],
        "accessories": [
            {
                "id": key.replace(" ", "_"),
                "name": val["name"],
                "name_en": key,
            }
            for key, val in ACCESSORIES.items()
        ],
        "music_moods": [
            {
                "id": key,
                "name": val["name"],
                "description": val["description"],
            }
            for key, val in MUSIC_MOODS.items()
        ],
        "video_motion_styles": [
            {
                "id": key,
                "name": val["name"],
                "description": val["description"],
            }
            for key, val in VIDEO_MOTION_STYLES.items()
        ],
        # TTS 音色选项
        "tts_voices": QwenTTSService.get_voice_options(),
        # 视频生成选项
        "video_options": WanxVideoService.get_video_options(),
    }
