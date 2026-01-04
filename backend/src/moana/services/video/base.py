# src/moana/services/video/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class VideoAspectRatio(str, Enum):
    """Video aspect ratio presets."""
    LANDSCAPE_16_9 = "16:9"    # 横屏 1920x1080
    LANDSCAPE_4_3 = "4:3"      # 横屏 1440x1080
    PORTRAIT_9_16 = "9:16"     # 竖屏 1080x1920
    PORTRAIT_3_4 = "3:4"       # 竖屏 1080x1440
    SQUARE_1_1 = "1:1"         # 正方形 1080x1080


class VideoResolution(str, Enum):
    """Video resolution presets."""
    HD_720P = "720P"           # 1280x720
    FHD_1080P = "1080P"        # 1920x1080
    UHD_4K = "4K"              # 3840x2160 (部分 provider 支持)


class VideoMotionMode(str, Enum):
    """Video motion/camera movement styles."""
    STATIC = "static"          # 静态，几乎无运动
    SLOW = "slow"              # 缓慢运动
    NORMAL = "normal"          # 正常运动
    DYNAMIC = "dynamic"        # 动态，较多运动
    CINEMATIC = "cinematic"    # 电影感镜头运动


@dataclass
class VideoResult:
    """Result of video generation."""
    video_url: str
    duration: float  # in seconds
    thumbnail_url: str
    model: str
    resolution: str = "720P"
    aspect_ratio: str = "16:9"
    format: str = "mp4"
    has_audio: bool = True
    fps: int = 24


class BaseVideoService(ABC):
    """Abstract base class for video generation services."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int = 5,
        last_frame_url: str | None = None,
        # New parameters for enhanced service
        scene_template: str | None = None,
        character_ids: list[str] | None = None,
        reference_images: list[str] | None = None,
        auto_enhance_prompt: bool = True,
        negative_prompt: str | None = None,
    ) -> VideoResult:
        """Generate video from image(s).

        Args:
            image_url: URL of the source image (first frame)
            prompt: Text description for video generation
            duration_seconds: Target video duration
            last_frame_url: URL of the last frame image (optional, for smoother transitions)
            scene_template: Scene template ID for preset parameters
            character_ids: Character IDs for reference image lookup
            reference_images: Direct reference image URLs (max 3)
            auto_enhance_prompt: Whether to auto-enhance the prompt
            negative_prompt: Things to exclude from generation

        Returns:
            VideoResult with generated video details
        """
        pass

    @classmethod
    def get_config_options(cls) -> dict:
        """获取视频配置选项（供前端使用）."""
        return {
            "aspect_ratios": [
                {"value": "16:9", "label": "横屏 16:9", "description": "视频、电影", "recommended": True},
                {"value": "9:16", "label": "竖屏 9:16", "description": "手机、短视频"},
                {"value": "4:3", "label": "横屏 4:3", "description": "传统视频"},
                {"value": "3:4", "label": "竖屏 3:4", "description": "社交媒体"},
                {"value": "1:1", "label": "正方形 1:1", "description": "Instagram"},
            ],
            "resolutions": [
                {"value": "720P", "label": "720P 高清", "pixels": "1280x720", "recommended": True},
                {"value": "1080P", "label": "1080P 全高清", "pixels": "1920x1080"},
            ],
            "durations": [
                {"value": 5, "label": "5秒", "description": "快速预览", "recommended": True},
                {"value": 8, "label": "8秒", "description": "标准 (Veo 最大)", "provider_max": "veo"},
                {"value": 10, "label": "10秒", "description": "较长动画", "provider_max": "wanx"},
                {"value": 15, "label": "15秒", "description": "完整片段", "provider_max": "wanx"},
            ],
            "motion_modes": [
                {"value": "static", "label": "静态", "description": "几乎无运动，适合展示"},
                {"value": "slow", "label": "缓慢", "description": "轻微运动，适合氛围"},
                {"value": "normal", "label": "正常", "description": "自然运动", "recommended": True},
                {"value": "dynamic", "label": "动态", "description": "较多运动，适合动作"},
                {"value": "cinematic", "label": "电影感", "description": "电影级镜头运动"},
            ],
            "audio_options": [
                {"value": True, "label": "启用音效", "description": "AI 生成配套音效", "recommended": True},
                {"value": False, "label": "静音", "description": "无声视频"},
            ],
        }
