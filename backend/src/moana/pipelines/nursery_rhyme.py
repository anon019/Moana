# src/moana/pipelines/nursery_rhyme.py
"""Nursery rhyme generation pipeline.

V2 design (2025-12):
- Prompt enhancement with Gemini
- Suno V5 free mode for music generation
- Use Suno cover directly
- Full-chain logging with GenerationLogger
"""
import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from moana.services.music import get_music_service
from moana.services.music.base import MusicStyle
from moana.services.prompt import PromptEnhancer
from moana.services.logging import GenerationLogger
from moana.models.generation_log import GenerationStep

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Progress tracking for generation."""
    stage: str
    current: int
    total: int
    message: str


class NurseryRhymePipeline:
    """Pipeline for generating complete nursery rhymes.

    Uses Suno V5 free mode with Gemini prompt enhancement.
    Suno AI handles both lyrics and music creation.
    """

    def __init__(self, music_service: Any | None = None):
        self._music_service = music_service or get_music_service()

    async def generate(
        self,
        params: dict[str, Any],
        music_style: MusicStyle = MusicStyle.CHEERFUL,
        on_progress: Callable[[GenerationProgress], None] | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a complete nursery rhyme with audio and cover.

        Args:
            params: All request parameters dict, passed to PromptEnhancer
            music_style: Music style enum (fallback)
            on_progress: Progress callback
            task_id: Task ID for logging

        Returns:
            Dict containing song info, audio URL, cover URL, etc.
        """
        # Extract required parameters
        child_name = params.get("child_name", "宝宝")
        age_months = params.get("age_months", 36)
        theme_topic = params.get("theme_topic", "")
        creation_mode = params.get("creation_mode", "preset")
        custom_prompt = params.get("custom_prompt")
        favorite_characters = params.get("favorite_characters")

        # Ensure music_mood has value
        if not params.get("music_mood"):
            params["music_mood"] = music_style.value

        # Initialize logger
        log_task_id = task_id or str(uuid4())
        gen_logger = GenerationLogger(task_id=log_task_id)

        logger.info(f"Generating nursery rhyme: {theme_topic}, mode={creation_mode}, params={len(params)}")

        # Log initialization
        await gen_logger.log_step(
            step=GenerationStep.INIT,
            message=f"开始生成儿歌，共 {len(params)} 个参数",
            input_params=params,
        )

        if on_progress:
            on_progress(GenerationProgress("init", 0, 3, "正在增强提示词..."))

        # Step 1: Prompt enhancement
        enhancer = PromptEnhancer()
        enhance_result = await enhancer.enhance(params)

        await gen_logger.log_step(
            step=GenerationStep.PROMPT_ENHANCE,
            message="提示词增强完成",
            input_params={"template": enhance_result.template_prompt},
            output_result={
                "enhanced": enhance_result.enhanced_prompt,
                "length": len(enhance_result.enhanced_prompt),
            },
            duration=enhance_result.duration_ms / 1000,
        )

        if on_progress:
            on_progress(GenerationProgress("music", 1, 3, "Suno 正在创作音乐..."))

        # Step 2: Generate music with Suno
        callback_id = task_id or log_task_id
        music_result = await self._music_service.generate(
            prompt=enhance_result.enhanced_prompt,
            style=music_style,
            callback_task_id=callback_id,
        )

        await gen_logger.log_step(
            step=GenerationStep.MUSIC_GENERATE,
            message="音乐生成完成",
            input_params={"prompt": enhance_result.enhanced_prompt[:200]},
            output_result={
                "audio_url": music_result.audio_url,
                "duration": music_result.duration,
                "tracks_count": len(music_result.extra.get("all_tracks", [])),
            },
        )

        if on_progress:
            on_progress(GenerationProgress("complete", 3, 3, "生成完成"))

        # Extract all tracks (Suno returns 2)
        all_tracks = music_result.extra.get("all_tracks", [])
        primary_cover = music_result.extra.get("primary_cover_url", "")  # 优先本地，备用 Suno 原始
        primary_suno_cover = music_result.extra.get("primary_suno_cover_url", "")  # Suno 原始封面 URL
        primary_video = music_result.extra.get("primary_video_url", "")
        primary_timestamped_lyrics = music_result.extra.get("primary_timestamped_lyrics", [])

        # Build user_selections for storage
        user_selections = {k: v for k, v in params.items() if v is not None}

        # Log completion
        # 生成标题 - 不带定语，直接用主题
        song_title = f"{theme_topic}之歌" if theme_topic else "儿歌"

        await gen_logger.log_step(
            step=GenerationStep.COMPLETE,
            message="儿歌生成完成",
            output_result={
                "title": song_title,
                "duration": music_result.duration,
                "tracks": len(all_tracks),
            },
        )

        return {
            "title": song_title,
            "theme_topic": theme_topic,
            "educational_goal": f"通过儿歌帮助孩子学习{theme_topic}",
            "lyrics": {
                "full_text": music_result.lyrics,
                "timestamped": primary_timestamped_lyrics,
                "sections": [],
                "prompt": enhance_result.enhanced_prompt,
            },
            "audio_url": music_result.audio_url,
            "audio_duration": music_result.duration,
            "video_url": primary_video,
            "cover_url": primary_cover,  # 优先本地，备用 Suno 原始
            "suno_cover_url": primary_suno_cover,  # Suno 原始封面 URL（始终保存）
            "all_tracks": all_tracks,
            "personalization": {
                "child_name": child_name,
                "favorite_characters": favorite_characters or [],
            },
            "user_selections": user_selections,
            "user_prompt": custom_prompt,
            "enhanced_prompt": enhance_result.enhanced_prompt,
            "generated_by": {
                "prompt_model": enhance_result.model,
                "music_model": music_result.model,
            },
            "generation_mode": "suno_free",
            "task_id": music_result.extra.get("task_id", ""),
        }

    # Alias for backward compatibility
    generate_v2 = generate
