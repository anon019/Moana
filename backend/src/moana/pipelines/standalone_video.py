"""Standalone video generation pipeline."""
import logging
from dataclasses import dataclass
from typing import Callable

from moana.services.image import get_image_service
from moana.services.video import get_video_service
from moana.services.smart import SmartPromptAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class StandaloneVideoProgress:
    """Progress tracking for standalone video generation."""
    stage: str
    progress: int
    message: str


class StandaloneVideoPipeline:
    """Pipeline for generating standalone videos from user prompts."""

    def __init__(self):
        self._image_service = get_image_service()
        self._video_service = get_video_service()
        self._prompt_analyzer = SmartPromptAnalyzer()

    async def generate(
        self,
        child_name: str,
        age_months: int,
        custom_prompt: str,
        first_frame_url: str | None = None,
        generate_first_frame: bool = True,
        aspect_ratio: str = "16:9",
        resolution: str = "720P",
        duration_seconds: int = 5,
        motion_mode: str = "normal",
        art_style: str = "storybook",
        auto_enhance_prompt: bool = True,
        negative_prompt: str | None = None,
        scene_template: str | None = None,
        on_progress: Callable[[StandaloneVideoProgress], None] | None = None,
    ) -> dict:
        """Generate standalone video from user prompt.

        Args:
            child_name: Child's name
            age_months: Child's age in months
            custom_prompt: User's video description
            first_frame_url: Existing first frame URL (optional)
            generate_first_frame: Auto-generate first frame if no URL
            aspect_ratio: Video aspect ratio
            resolution: Video resolution
            duration_seconds: Video duration (4-8s)
            motion_mode: Motion style
            art_style: Art style for first frame
            auto_enhance_prompt: Whether to enhance prompt with AI
            negative_prompt: Things to avoid
            scene_template: Scene template ID
            on_progress: Progress callback

        Returns:
            Dict with video_url, thumbnail_url, and metadata
        """
        # Stage 1: Analyze prompt
        if on_progress:
            on_progress(StandaloneVideoProgress("analyzing", 5, "分析创意描述..."))

        analysis = await self._prompt_analyzer.analyze(
            custom_prompt=custom_prompt,
            child_name=child_name,
            age_months=age_months,
            content_type="video",
        )

        # Stage 2: Generate or use first frame
        if on_progress:
            on_progress(StandaloneVideoProgress("first_frame", 20, "生成首帧图片..."))

        if first_frame_url:
            frame_url = first_frame_url
            logger.info(f"Using provided first frame: {frame_url[:50]}...")
        elif generate_first_frame:
            # Generate first frame
            width = 1280 if aspect_ratio == "16:9" else 1024
            height = 720 if aspect_ratio == "16:9" else 1024

            result = await self._image_service.generate(
                prompt=analysis.enhanced_prompt,
                width=width,
                height=height,
            )
            frame_url = result.url
            logger.info(f"Generated first frame: {frame_url[:50]}...")
        else:
            raise ValueError("Must provide first_frame_url or set generate_first_frame=True")

        # Stage 3: Generate video
        if on_progress:
            on_progress(StandaloneVideoProgress("video", 40, "生成视频中..."))

        video_prompt = analysis.enhanced_prompt if auto_enhance_prompt else custom_prompt

        # Veo 3.1 要求 duration 在 4-8 秒范围内
        safe_duration = max(4, min(duration_seconds, 8))

        video_result = await self._video_service.generate(
            image_url=frame_url,
            prompt=video_prompt,
            duration_seconds=safe_duration,
            scene_template=scene_template,
            auto_enhance_prompt=auto_enhance_prompt,
            negative_prompt=negative_prompt,
        )

        if on_progress:
            on_progress(StandaloneVideoProgress("complete", 100, "生成完成"))

        return {
            "title": analysis.title,
            "video_url": video_result.video_url,
            "thumbnail_url": frame_url,
            "first_frame_url": frame_url,
            "duration": video_result.duration,
            "theme_category": analysis.theme_category,
            "theme_topic": analysis.theme_topic,
            "custom_prompt": custom_prompt,
            "prompt_enhanced": analysis.enhanced_prompt,
            "educational_goal": analysis.educational_goal,
            "personalization": {
                "child_name": child_name,
                "age_months": age_months,
            },
            "generated_by": {
                "video_model": video_result.model,
                "image_model": getattr(self._image_service, '_model', 'unknown'),
            },
        }
