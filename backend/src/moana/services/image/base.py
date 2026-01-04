from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class ImageStyle(str, Enum):
    """Image style presets - supports all Nano Banana Pro styles."""

    # === 儿童内容风格 ===
    STORYBOOK = "storybook"          # 绘本插画风格
    CARTOON = "cartoon"              # 卡通风格
    WATERCOLOR = "watercolor"        # 水彩风格
    FLAT = "flat"                    # 扁平设计

    # === 3D 风格 ===
    THREE_D_RENDER = "3d_render"     # 3D 渲染
    THREE_D_CARTOON = "3d_cartoon"   # 3D 卡通
    CLAY = "clay"                    # 粘土/黏土风格
    PIXAR = "pixar"                  # 皮克斯风格
    FIGURINE = "figurine"            # 3D 手办/公仔

    # === 动漫风格 ===
    ANIME = "anime"                  # 日式动漫
    CHIBI = "chibi"                  # Q版/萌系
    MANGA = "manga"                  # 漫画风格
    GHIBLI = "ghibli"                # 吉卜力风格

    # === 写实风格 ===
    PHOTOREALISTIC = "photorealistic"  # 照片写实
    CINEMATIC = "cinematic"            # 电影感
    PORTRAIT = "portrait"              # 人像摄影

    # === 艺术风格 ===
    OIL_PAINTING = "oil_painting"    # 油画
    SKETCH = "sketch"                # 素描
    INK_WASH = "ink_wash"            # 水墨画
    PIXEL_ART = "pixel_art"          # 像素艺术
    VECTOR = "vector"                # 矢量图形
    POP_ART = "pop_art"              # 波普艺术

    # === 特殊风格 ===
    CYBERPUNK = "cyberpunk"          # 赛博朋克
    FANTASY = "fantasy"              # 奇幻风格
    VINTAGE = "vintage"              # 复古风格
    MINIMALIST = "minimalist"        # 极简风格
    SURREAL = "surreal"              # 超现实

    # === 无风格增强 ===
    NONE = "none"                    # 不添加风格修饰，纯用户 prompt


@dataclass
class ImageResult:
    """Result of image generation."""
    url: str
    prompt: str
    revised_prompt: str | None = None
    model: str = ""
    width: int = 1024
    height: int = 1024
    thumb_url: str | None = None


class BaseImageService(ABC):
    """Abstract base class for image generation services."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.STORYBOOK,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: str | None = None,
    ) -> ImageResult:
        """Generate an image from prompt."""
        pass

    def enhance_prompt_for_children(
        self,
        prompt: str,
        style: ImageStyle,
        safe_mode: bool = True,
    ) -> str:
        """Enhance prompt with style modifiers.

        Args:
            prompt: Original user prompt
            style: Image style preset
            safe_mode: If True, add child-safety prompt (default for kids content)
        """
        style_modifiers = {
            # 儿童内容风格
            ImageStyle.STORYBOOK: "children's book illustration, warm colors, whimsical style, soft lighting",
            ImageStyle.CARTOON: "cute cartoon style, vibrant colors, friendly characters, clean lines",
            ImageStyle.WATERCOLOR: "soft watercolor illustration, gentle colors, dreamy atmosphere, artistic",
            ImageStyle.FLAT: "flat design illustration, simple geometric shapes, bold colors, minimal",

            # 3D 风格
            ImageStyle.THREE_D_RENDER: "3D rendered, high quality 3D graphics, realistic lighting, detailed textures",
            ImageStyle.THREE_D_CARTOON: "3D cartoon style, Pixar-like render, soft shadows, vibrant colors",
            ImageStyle.CLAY: "clay animation style, claymation, soft rounded shapes, handmade look",
            ImageStyle.PIXAR: "Pixar animation style, 3D rendered, expressive characters, cinematic lighting",
            ImageStyle.FIGURINE: "3D figurine, collectible toy style, detailed miniature, studio photography",

            # 动漫风格
            ImageStyle.ANIME: "anime style, Japanese animation, detailed eyes, clean lines, vibrant colors",
            ImageStyle.CHIBI: "chibi style, super deformed, cute big head, small body, kawaii",
            ImageStyle.MANGA: "manga style, black and white, dramatic shading, Japanese comic art",
            ImageStyle.GHIBLI: "Studio Ghibli style, hand-drawn animation, soft colors, magical atmosphere",

            # 写实风格
            ImageStyle.PHOTOREALISTIC: "photorealistic, ultra detailed, 8K resolution, professional photography",
            ImageStyle.CINEMATIC: "cinematic, movie still, dramatic lighting, film grain, widescreen",
            ImageStyle.PORTRAIT: "portrait photography, professional lighting, shallow depth of field, detailed",

            # 艺术风格
            ImageStyle.OIL_PAINTING: "oil painting, classical art style, rich textures, visible brushstrokes",
            ImageStyle.SKETCH: "pencil sketch, hand-drawn, detailed linework, artistic shading",
            ImageStyle.INK_WASH: "Chinese ink wash painting, sumi-e style, elegant brushwork, minimalist",
            ImageStyle.PIXEL_ART: "pixel art, 16-bit style, retro game graphics, crisp pixels",
            ImageStyle.VECTOR: "vector illustration, clean lines, flat colors, scalable graphics",
            ImageStyle.POP_ART: "pop art style, bold colors, Ben-Day dots, Andy Warhol inspired",

            # 特殊风格
            ImageStyle.CYBERPUNK: "cyberpunk style, neon lights, futuristic, dark atmosphere, sci-fi",
            ImageStyle.FANTASY: "fantasy art, magical, ethereal lighting, mystical atmosphere",
            ImageStyle.VINTAGE: "vintage style, retro aesthetic, aged colors, nostalgic feel",
            ImageStyle.MINIMALIST: "minimalist design, simple composition, clean, lots of white space",
            ImageStyle.SURREAL: "surrealist art, dreamlike, impossible geometry, Salvador Dali inspired",

            # 无风格
            ImageStyle.NONE: "",
        }

        style_mod = style_modifiers.get(style, "")

        # 构建最终 prompt
        parts = [prompt]
        if style_mod:
            parts.append(style_mod)

        if safe_mode:
            safety_prompt = "child-friendly, safe for kids, no scary elements, no violence"
            parts.append(safety_prompt)

        return ", ".join(parts)
