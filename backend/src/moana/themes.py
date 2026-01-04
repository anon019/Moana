"""主题配置模块 - 定义所有可用的教育主题."""
from dataclasses import dataclass
from typing import Literal


@dataclass
class Theme:
    """教育主题配置."""
    id: str                     # 唯一标识
    name: str                   # 显示名称
    category: Literal["habit", "cognition"]  # 分类
    subcategory: str            # 子分类
    age_range: tuple[int, int]  # 适合月龄范围 (min, max)
    keywords: list[str]         # 关联关键词
    default_story_hint: str     # 默认绘本创作提示
    default_song_hint: str      # 默认儿歌创作提示


# 主题注册表
THEME_REGISTRY: dict[str, Theme] = {
    # ========== 习惯养成 - 生活自理 ==========
    "brush_teeth": Theme(
        id="brush_teeth",
        name="刷牙",
        category="habit",
        subcategory="生活自理",
        age_range=(12, 48),
        keywords=["刷牙", "牙齿", "牙刷", "牙膏"],
        default_story_hint="小动物学刷牙，强调早晚刷、上下左右刷",
        default_song_hint="欢快节奏的刷牙歌，朗朗上口",
    ),
    "wash_hands": Theme(
        id="wash_hands",
        name="洗手",
        category="habit",
        subcategory="生活自理",
        age_range=(12, 48),
        keywords=["洗手", "肥皂", "细菌", "干净"],
        default_story_hint="饭前便后要洗手，七步洗手法",
        default_song_hint="洗手歌，边唱边洗",
    ),
    "get_dressed": Theme(
        id="get_dressed",
        name="穿衣",
        category="habit",
        subcategory="生活自理",
        age_range=(18, 48),
        keywords=["穿衣", "穿衣服", "袜子", "鞋子", "自己穿"],
        default_story_hint="小朋友学穿衣，先穿什么后穿什么",
        default_song_hint="穿衣歌，唱出穿衣顺序",
    ),
    "potty_training": Theme(
        id="potty_training",
        name="如厕",
        category="habit",
        subcategory="生活自理",
        age_range=(18, 42),
        keywords=["如厕", "上厕所", "马桶", "尿尿", "便便"],
        default_story_hint="小动物学用马桶，不再用尿布",
        default_song_hint="如厕歌，鼓励自己上厕所",
    ),
    # ========== 习惯养成 - 饮食习惯 ==========
    "eat_independently": Theme(
        id="eat_independently",
        name="自己吃饭",
        category="habit",
        subcategory="饮食习惯",
        age_range=(12, 36),
        keywords=["吃饭", "自己吃", "勺子", "筷子"],
        default_story_hint="小朋友学用勺子/筷子自己吃饭",
        default_song_hint="吃饭歌，一口一口吃光光",
    ),
    "no_picky_eating": Theme(
        id="no_picky_eating",
        name="不挑食",
        category="habit",
        subcategory="饮食习惯",
        age_range=(18, 48),
        keywords=["挑食", "蔬菜", "不爱吃", "营养"],
        default_story_hint="蔬菜水果都是好朋友，不挑食长得高",
        default_song_hint="不挑食歌，各种食物都尝尝",
    ),
    # ========== 习惯养成 - 作息规律 ==========
    "bedtime": Theme(
        id="bedtime",
        name="按时睡觉",
        category="habit",
        subcategory="作息规律",
        age_range=(12, 48),
        keywords=["睡觉", "睡前", "晚安", "做梦"],
        default_story_hint="太阳下山月亮出来，小动物们都睡觉了",
        default_song_hint="摇篮曲风格，温柔舒缓",
    ),
    "nap_time": Theme(
        id="nap_time",
        name="午睡",
        category="habit",
        subcategory="作息规律",
        age_range=(12, 48),
        keywords=["午睡", "午觉", "休息"],
        default_story_hint="中午休息一下，下午更有精神",
        default_song_hint="轻柔的午睡歌",
    ),
    # ========== 习惯养成 - 社交礼仪 ==========
    "sharing": Theme(
        id="sharing",
        name="分享",
        category="habit",
        subcategory="社交礼仪",
        age_range=(24, 48),
        keywords=["分享", "一起玩", "好朋友"],
        default_story_hint="好朋友一起分享玩具，更快乐",
        default_song_hint="分享歌，分享让快乐翻倍",
    ),
    "greeting": Theme(
        id="greeting",
        name="打招呼",
        category="habit",
        subcategory="社交礼仪",
        age_range=(12, 36),
        keywords=["打招呼", "你好", "再见", "礼貌"],
        default_story_hint="见面说你好，分别说再见",
        default_song_hint="礼貌歌，常用礼貌用语",
    ),
    "tidy_up": Theme(
        id="tidy_up",
        name="收拾玩具",
        category="habit",
        subcategory="社交礼仪",
        age_range=(18, 48),
        keywords=["收拾", "整理", "玩具", "归位"],
        default_story_hint="玩完玩具要归位，做个整洁的好宝宝",
        default_song_hint="收拾歌，玩具回家了",
    ),
    # ========== 认知世界 - 基础认知 ==========
    "colors": Theme(
        id="colors",
        name="颜色",
        category="cognition",
        subcategory="基础认知",
        age_range=(12, 36),
        keywords=["颜色", "红色", "蓝色", "黄色", "绿色"],
        default_story_hint="认识各种颜色，在生活中找颜色",
        default_song_hint="颜色歌，红橙黄绿蓝",
    ),
    "shapes": Theme(
        id="shapes",
        name="形状",
        category="cognition",
        subcategory="基础认知",
        age_range=(18, 42),
        keywords=["形状", "圆形", "方形", "三角形"],
        default_story_hint="认识基础形状，生活中的形状",
        default_song_hint="形状歌，圆圆方方三角形",
    ),
    "numbers": Theme(
        id="numbers",
        name="数字",
        category="cognition",
        subcategory="基础认知",
        age_range=(24, 48),
        keywords=["数字", "数数", "1234", "几个"],
        default_story_hint="从1数到10，数数小动物",
        default_song_hint="数字歌，1像铅笔2像鸭",
    ),
    "big_small": Theme(
        id="big_small",
        name="大小",
        category="cognition",
        subcategory="基础认知",
        age_range=(12, 36),
        keywords=["大小", "大的", "小的", "比较"],
        default_story_hint="比较大小，大象和蚂蚁",
        default_song_hint="大小歌，大大小小比一比",
    ),
    # ========== 认知世界 - 自然世界 ==========
    "animals": Theme(
        id="animals",
        name="动物",
        category="cognition",
        subcategory="自然世界",
        age_range=(12, 48),
        keywords=["动物", "小狗", "小猫", "小鸟", "农场"],
        default_story_hint="认识各种动物，动物的叫声和特点",
        default_song_hint="动物歌，学动物叫声",
    ),
    "plants": Theme(
        id="plants",
        name="植物",
        category="cognition",
        subcategory="自然世界",
        age_range=(18, 48),
        keywords=["植物", "花", "树", "草", "种子"],
        default_story_hint="种子发芽长大开花，植物的生长",
        default_song_hint="植物歌，小种子发芽了",
    ),
    "weather": Theme(
        id="weather",
        name="天气",
        category="cognition",
        subcategory="自然世界",
        age_range=(18, 48),
        keywords=["天气", "晴天", "雨天", "下雪", "刮风"],
        default_story_hint="各种天气现象，下雨打伞",
        default_song_hint="天气歌，太阳雨滴和雪花",
    ),
    # ========== 认知世界 - 社会认知 ==========
    "family": Theme(
        id="family",
        name="家庭成员",
        category="cognition",
        subcategory="社会认知",
        age_range=(12, 36),
        keywords=["家庭", "爸爸", "妈妈", "爷爷", "奶奶"],
        default_story_hint="认识家庭成员，爱家人",
        default_song_hint="家庭歌，我爱我的家",
    ),
    "occupations": Theme(
        id="occupations",
        name="职业",
        category="cognition",
        subcategory="社会认知",
        age_range=(24, 48),
        keywords=["职业", "医生", "老师", "警察", "消防员"],
        default_story_hint="认识各种职业，职业的工作内容",
        default_song_hint="职业歌，长大想当什么",
    ),
    "vehicles": Theme(
        id="vehicles",
        name="交通工具",
        category="cognition",
        subcategory="社会认知",
        age_range=(18, 48),
        keywords=["交通工具", "汽车", "火车", "飞机", "轮船"],
        default_story_hint="各种交通工具，它们怎么走",
        default_song_hint="交通工具歌，汽车嘟嘟火车呜呜",
    ),
    # ========== 认知世界 - 情绪认知 ==========
    "happy": Theme(
        id="happy",
        name="开心",
        category="cognition",
        subcategory="情绪认知",
        age_range=(18, 48),
        keywords=["开心", "快乐", "高兴", "笑"],
        default_story_hint="什么事情让你开心，开心的表情",
        default_song_hint="开心歌，笑一笑",
    ),
    "sad": Theme(
        id="sad",
        name="难过",
        category="cognition",
        subcategory="情绪认知",
        age_range=(18, 48),
        keywords=["难过", "伤心", "哭", "不开心"],
        default_story_hint="难过的时候怎么办，拥抱安慰",
        default_song_hint="情绪歌，难过也没关系",
    ),
    "angry": Theme(
        id="angry",
        name="生气",
        category="cognition",
        subcategory="情绪认知",
        age_range=(24, 48),
        keywords=["生气", "发脾气", "愤怒"],
        default_story_hint="生气的时候深呼吸，学会控制情绪",
        default_song_hint="冷静歌，生气的时候数到10",
    ),
    "scared": Theme(
        id="scared",
        name="害怕",
        category="cognition",
        subcategory="情绪认知",
        age_range=(18, 48),
        keywords=["害怕", "恐惧", "怕黑", "勇敢"],
        default_story_hint="害怕是正常的，勇敢面对",
        default_song_hint="勇敢歌，不怕不怕我最勇敢",
    ),
}


def get_themes_by_category(category: str) -> list[Theme]:
    """获取指定分类的所有主题."""
    return [t for t in THEME_REGISTRY.values() if t.category == category]


def get_themes_for_age(age_months: int) -> list[Theme]:
    """获取适合指定月龄的主题."""
    return [
        t for t in THEME_REGISTRY.values()
        if t.age_range[0] <= age_months <= t.age_range[1]
    ]


def find_theme_by_keyword(keyword: str) -> Theme | None:
    """根据关键词查找主题."""
    for theme in THEME_REGISTRY.values():
        if keyword in theme.name or keyword in theme.keywords:
            return theme
    return None


def get_all_themes() -> list[Theme]:
    """获取所有主题."""
    return list(THEME_REGISTRY.values())
