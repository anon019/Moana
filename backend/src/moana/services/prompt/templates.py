# src/moana/services/prompt/templates.py
"""Template builders for nursery rhyme prompt enhancement.

V2 redesign: 支持动态参数处理，无需修改代码即可支持新参数。
所有参数通过 PARAM_CATEGORIES 分类，自动生成提示词模板。
"""

from typing import Any


def get_age_description(age_months: int) -> str:
    """Get age description in Chinese."""
    if age_months < 24:
        return "1-2岁宝宝"
    elif age_months < 36:
        return "2-3岁幼儿"
    elif age_months < 48:
        return "3-4岁儿童"
    else:
        return "4-6岁儿童"


# 参数分类配置：定义每个分类包含的参数和显示名称
# 新增参数只需在这里添加即可，无需修改其他代码
PARAM_CATEGORIES = {
    "music_style": {
        "title": "音乐风格",
        "params": {
            "music_mood": "情绪",
            "music_genre": "流派",
            "tempo": "节奏BPM",
            "energy_level": "能量强度",
        },
    },
    "vocal": {
        "title": "人声设置",
        "params": {
            "vocal_type": "人声类型",
            "vocal_gender": "人声性别",
            "vocal_range": "音域",
            "vocal_emotion": "情感表达",
            "vocal_style": "演唱风格",
            "vocal_effects": "声音效果",
            "vocal_regional": "地域特色",
        },
    },
    "instruments": {
        "title": "乐器与音效",
        "params": {
            "instruments": "乐器",
            "sound_effects": "音效",
        },
    },
    "lyrics": {
        "title": "歌词设置",
        "params": {
            "lyric_complexity": "歌词复杂度",
            "repetition_level": "重复程度",
        },
    },
    "structure": {
        "title": "歌曲结构",
        "params": {
            "song_structure": "结构类型",
            "duration_preference": "时长偏好",
            "action_types": "互动动作",
            "has_actions": "包含互动",
        },
    },
    "language": {
        "title": "语言文化",
        "params": {
            "language": "语言",
            "cultural_style": "文化风格",
        },
    },
    "personalization": {
        "title": "个性化",
        "params": {
            "educational_focus": "教育目标",
            "favorite_characters": "喜欢的角色",
            "favorite_colors": "喜欢的颜色",
            "favorite_animals": "喜欢的动物",
        },
    },
    "suno_advanced": {
        "title": "Suno进阶控制",
        "params": {
            "style_weight": "风格权重",
            "creativity": "创意程度",
            "negative_tags": "排除标签",
            "style_description": "风格描述",
            "seed": "随机种子",
        },
    },
}


def format_param_value(value: Any) -> str:
    """Format parameter value for display.

    处理各种类型的参数值：
    - list -> 逗号分隔的字符串
    - bool -> 是/否
    - number -> 字符串
    - None -> 跳过
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return "、".join(str(v) for v in value[:5])  # 最多5个
    if isinstance(value, bool):
        return "是" if value else "否"
    return str(value)


def build_dynamic_template(params: dict, mode: str = "preset") -> str:
    """Build template dynamically from any parameters.

    根据传入的参数自动生成模板，支持任意新增参数。
    注意：child_name 不传递给提示词增强，歌曲中不出现孩子名字。

    Args:
        params: 所有请求参数
        mode: 创作模式 (preset/smart)

    Returns:
        生成的模板字符串
    """
    age_months = params.get("age_months", 36)
    theme_topic = params.get("theme_topic", "")
    theme_category = params.get("theme_category", "habit")
    custom_prompt = params.get("custom_prompt", "")

    age_desc = get_age_description(age_months)
    category_desc = "习惯养成" if theme_category == "habit" else "认知启蒙"

    # 构建基础信息 - 不包含 child_name
    if mode == "smart" and custom_prompt:
        template = f"""为{age_desc}创作儿歌。

【用户创意】
{custom_prompt}

【基本信息】
- 年龄段：{age_desc}
"""
    else:
        template = f"""为{age_desc}创作一首关于「{theme_topic}」的中文儿歌。

【基本信息】
- 年龄段：{age_desc}
- 主题类别：{category_desc}
"""

    # 动态添加各分类参数
    for category_id, category_config in PARAM_CATEGORIES.items():
        category_params = category_config["params"]
        category_lines = []

        for param_key, param_label in category_params.items():
            if param_key in params and params[param_key] is not None:
                value = format_param_value(params[param_key])
                if value:
                    category_lines.append(f"- {param_label}：{value}")

        if category_lines:
            template += f"\n【{category_config['title']}】\n"
            template += "\n".join(category_lines) + "\n"

    # 添加未分类的额外参数（支持前端新增参数）
    known_params = {"child_name", "age_months", "theme_topic", "theme_category",
                    "creation_mode", "custom_prompt", "music_style",
                    "art_style", "protagonist_animal", "protagonist_color",
                    "protagonist_accessory", "color_palette"}

    for category_config in PARAM_CATEGORIES.values():
        known_params.update(category_config["params"].keys())

    extra_params = []
    for key, value in params.items():
        if key not in known_params and value is not None:
            formatted = format_param_value(value)
            if formatted:
                # 将下划线转为空格，首字母大写
                label = key.replace("_", " ").title()
                extra_params.append(f"- {label}：{formatted}")

    if extra_params:
        template += "\n【其他设置】\n"
        template += "\n".join(extra_params) + "\n"

    return template


def build_preset_template(params: dict) -> str:
    """Build template for preset theme mode.

    Args:
        params: Dictionary with all parameters.

    Returns:
        Template string for Gemini enhancement.
    """
    return build_dynamic_template(params, mode="preset")


def build_smart_template(params: dict) -> str:
    """Build template for smart creation mode.

    Args:
        params: Dictionary with all parameters.

    Returns:
        Template string for Gemini enhancement.
    """
    return build_dynamic_template(params, mode="smart")
