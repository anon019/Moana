import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import logging

from moana.agents.story import StoryAgent, StyleConfig, StoryEnhancement, VisualEnhancement
from moana.agents.schemas import PictureBookOutline
from moana.services.image import get_image_service
from moana.services.image.base import BaseImageService, ImageStyle
from moana.services.tts import get_tts_service
from moana.services.tts.base import BaseTTSService
from moana.services.logging import GenerationLogger
from moana.models.generation_log import GenerationStep, LogLevel

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Progress tracking for generation."""
    stage: str
    current: int
    total: int
    message: str


class PictureBookPipeline:
    """Pipeline for generating complete picture books."""

    # 并发控制：限制同时进行的 TTS 请求数（避免触发阿里云 QPS 限制）
    TTS_CONCURRENCY_LIMIT = 2
    # 并发控制：限制同时进行的图片生成请求数
    IMAGE_CONCURRENCY_LIMIT = 3

    def __init__(
        self,
        story_agent: StoryAgent | None = None,
        image_service: BaseImageService | None = None,
        tts_service: BaseTTSService | None = None,
    ):
        self._story_agent = story_agent or StoryAgent()
        self._image_service = image_service or get_image_service()
        self._tts_service = tts_service or get_tts_service()
        # 信号量用于限制并发
        self._tts_semaphore = asyncio.Semaphore(self.TTS_CONCURRENCY_LIMIT)
        self._image_semaphore = asyncio.Semaphore(self.IMAGE_CONCURRENCY_LIMIT)

    async def generate(
        self,
        child_name: str,
        age_months: int,
        theme_topic: str,
        theme_category: str,
        favorite_characters: list[str] | None = None,
        voice_id: str | None = None,
        on_progress: Callable[[GenerationProgress], None] | None = None,
        # ===== 新增风格参数 =====
        art_style: str | None = None,
        protagonist_animal: str | None = None,
        protagonist_color: str | None = None,
        protagonist_accessory: str | None = None,
        color_palette: str | None = None,
        # ===== 新增增强参数 =====
        story_enhancement: dict | None = None,
        visual_enhancement: dict | None = None,
        # ===== 日志记录 =====
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a complete picture book with images and audio.

        Args:
            child_name: 孩子名字
            age_months: 孩子月龄
            theme_topic: 主题
            theme_category: 类别
            favorite_characters: 喜欢的角色
            voice_id: TTS 声音ID
            on_progress: 进度回调
            art_style: 美术风格 (pixar_3d, watercolor, flat_vector, crayon, anime)
            protagonist_animal: 主角动物 (bunny, bear, cat, dog, panda, fox)
            protagonist_color: 主角颜色 (white, brown, orange 等)
            protagonist_accessory: 主角配饰 (blue overalls, red scarf 等)
            color_palette: 色彩风格 (pastel, vibrant, warm, cool, monochrome)
            task_id: 任务 ID，用于日志记录
        """
        # 初始化日志记录器
        gen_logger = GenerationLogger(task_id=task_id) if task_id else None

        # 记录初始化
        if gen_logger:
            await gen_logger.log_step(
                step=GenerationStep.INIT,
                message="开始生成绘本",
                input_params={
                    "child_name": child_name,
                    "age_months": age_months,
                    "theme_topic": theme_topic,
                    "theme_category": theme_category,
                    "art_style": art_style,
                    "protagonist_animal": protagonist_animal,
                    "color_palette": color_palette,
                },
            )

        # 构建增强配置对象
        story_enh = None
        if story_enhancement:
            story_enh = StoryEnhancement(
                narrative_pace=story_enhancement.get("narrative_pace"),
                interaction_density=story_enhancement.get("interaction_density"),
                educational_focus=story_enhancement.get("educational_focus"),
                language_style=story_enhancement.get("language_style"),
                plot_complexity=story_enhancement.get("plot_complexity"),
                ending_style=story_enhancement.get("ending_style"),
            )

        visual_enh = None
        if visual_enhancement:
            visual_enh = VisualEnhancement(
                time_atmosphere=visual_enhancement.get("time_atmosphere"),
                scene_environment=visual_enhancement.get("scene_environment"),
                emotional_tone=visual_enhancement.get("emotional_tone"),
                composition_style=visual_enhancement.get("composition_style"),
                lighting_effect=visual_enhancement.get("lighting_effect"),
            )

        # 构建风格配置
        style_config = StyleConfig(
            art_style=art_style or "pixar_3d",
            protagonist_animal=protagonist_animal or "bunny",
            protagonist_color=protagonist_color or "white",
            protagonist_accessory=protagonist_accessory or "blue overalls",
            color_palette=color_palette or "pastel",
            story_enhancement=story_enh,
            visual_enhancement=visual_enh,
        )

        # Stage 1: Generate story outline
        if on_progress:
            on_progress(GenerationProgress("outline", 0, 1, "正在创作故事..."))

        story_start_time = time.time()
        try:
            outline = await self._story_agent.generate_outline(
                child_name=child_name,
                age_months=age_months,
                theme_topic=theme_topic,
                theme_category=theme_category,
                favorite_characters=favorite_characters,
                style_config=style_config,
            )
            story_duration = time.time() - story_start_time

            if gen_logger:
                await gen_logger.log_step(
                    step=GenerationStep.STORY_GENERATE,
                    message=f"故事大纲生成完成: {outline.title}",
                    input_params={"style_config": style_config.__dict__ if hasattr(style_config, '__dict__') else str(style_config)},
                    output_result={
                        "title": outline.title,
                        "page_count": len(outline.pages),
                        "educational_goal": outline.educational_goal,
                    },
                    duration=story_duration,
                )
        except Exception as e:
            if gen_logger:
                await gen_logger.log_error(
                    step=GenerationStep.STORY_GENERATE,
                    message="故事生成失败",
                    error=e,
                )
            raise

        if on_progress:
            on_progress(GenerationProgress("outline", 1, 1, "故事创作完成"))

        # Stage 2: Generate images for each page (parallel)
        if on_progress:
            on_progress(GenerationProgress("images", 0, len(outline.pages), "正在生成插图..."))

        images_start_time = time.time()
        image_tasks = [
            self._generate_page_image(page.image_prompt, i, len(outline.pages), on_progress, gen_logger)
            for i, page in enumerate(outline.pages)
        ]
        image_results = await asyncio.gather(*image_tasks)
        images_duration = time.time() - images_start_time

        if gen_logger:
            await gen_logger.log_step(
                step=GenerationStep.IMAGE_GENERATE,
                message=f"所有图片生成完成 ({len(image_results)} 张)",
                output_result={"image_count": len(image_results), "total_duration": images_duration},
                duration=images_duration,
            )

        # Stage 3: Generate audio for each page (parallel)
        if on_progress:
            on_progress(GenerationProgress("audio", 0, len(outline.pages), "正在生成朗读音频..."))

        audio_start_time = time.time()
        audio_tasks = [
            self._generate_page_audio(page.text, voice_id, i, len(outline.pages), on_progress, gen_logger)
            for i, page in enumerate(outline.pages)
        ]
        audio_results = await asyncio.gather(*audio_tasks)
        audio_duration = time.time() - audio_start_time

        if gen_logger:
            await gen_logger.log_step(
                step=GenerationStep.AUDIO_SYNTHESIZE,
                message=f"所有音频生成完成 ({len(audio_results)} 条)",
                output_result={"audio_count": len(audio_results), "total_duration": audio_duration},
                duration=audio_duration,
            )

        # Combine results
        pages = []
        total_duration = 0

        for i, page in enumerate(outline.pages):
            img_result = image_results[i]
            audio_result = audio_results[i]

            # 只存储每页的独有内容，通用配置（model/style/voice_id）由 style_config 和 generated_by 提供
            page_data = {
                "page_num": page.page_num,
                "text": page.text,
                "image_url": img_result.url,
                "image_thumb_url": img_result.thumb_url,
                "image_prompt": page.image_prompt,
                "audio_url": audio_result.audio_url,
                "audio_duration": audio_result.duration,
                "interaction": page.interaction.model_dump() if page.interaction else None,
            }
            pages.append(page_data)
            total_duration += audio_result.duration

        return {
            "title": outline.title,
            "theme_topic": outline.theme_topic,
            "educational_goal": outline.educational_goal,
            "pages": pages,
            "total_duration": total_duration,
            "total_interactions": outline.total_interactions,
            "personalization": {
                "child_name": child_name,
                "favorite_characters": favorite_characters or [],
            },
            "style_config": {
                "art_style": style_config.art_style,
                "protagonist_animal": style_config.protagonist_animal,
                "protagonist_color": style_config.protagonist_color,
                "protagonist_accessory": style_config.protagonist_accessory,
                "color_palette": style_config.color_palette,
            },
            "generated_by": {
                "story_model": self._story_agent._llm.model_name,
                "image_model": getattr(self._image_service, 'model_name', 'unknown'),
                "tts_model": getattr(self._tts_service, 'model_name', 'unknown'),
            },
        }

    async def _generate_page_image(
        self,
        prompt: str,
        index: int,
        total: int,
        on_progress: Callable[[GenerationProgress], None] | None,
        gen_logger: GenerationLogger | None = None,
    ):
        """Generate image for a single page with concurrency control.

        注意：使用 ImageStyle.NONE 是因为 StoryAgent 生成的 image_prompt
        已经包含了完整的风格描述（基于用户选择的 art_style）。
        这样前端传来的任何艺术风格都会透传到图片服务，不会被后端过滤。
        """
        async with self._image_semaphore:
            start_time = time.time()
            logger.debug(f"[PictureBook] Generating image {index+1}/{total}, prompt: {prompt[:100]}...")

            try:
                result = await self._image_service.generate(
                    prompt=prompt,
                    style=ImageStyle.NONE,
                )
                duration = time.time() - start_time

                if gen_logger:
                    await gen_logger.log_step(
                        step=GenerationStep.IMAGE_GENERATE,
                        message=f"图片 {index+1}/{total} 生成完成",
                        input_params={"prompt": prompt[:200], "page_index": index + 1},
                        output_result={"url": result.url, "model": getattr(result, 'model', 'unknown')},
                        duration=duration,
                    )
            except Exception as e:
                if gen_logger:
                    await gen_logger.log_error(
                        step=GenerationStep.IMAGE_GENERATE,
                        message=f"图片 {index+1}/{total} 生成失败",
                        error=e,
                        input_params={"prompt": prompt[:200], "page_index": index + 1},
                    )
                raise

            if on_progress:
                on_progress(GenerationProgress("images", index + 1, total, f"插图 {index + 1}/{total} 完成"))

            return result

    async def _generate_page_audio(
        self,
        text: str,
        voice_id: str | None,
        index: int,
        total: int,
        on_progress: Callable[[GenerationProgress], None] | None,
        gen_logger: GenerationLogger | None = None,
    ):
        """Generate audio for a single page with concurrency control."""
        async with self._tts_semaphore:
            start_time = time.time()
            # 增加请求间隔，进一步避免触发 QPS 限制
            await asyncio.sleep(0.5)

            try:
                result = await self._tts_service.synthesize(
                    text=text,
                    voice_id=voice_id,
                    speed=0.9,  # Slightly slower for children
                )
                duration = time.time() - start_time

                if gen_logger:
                    await gen_logger.log_step(
                        step=GenerationStep.AUDIO_SYNTHESIZE,
                        message=f"音频 {index+1}/{total} 合成完成",
                        input_params={"text": text, "voice_id": voice_id, "page_index": index + 1},
                        output_result={
                            "audio_url": result.audio_url,
                            "duration": result.duration,
                            "model": getattr(result, 'model', 'unknown'),
                        },
                        duration=duration,
                    )
            except Exception as e:
                if gen_logger:
                    await gen_logger.log_error(
                        step=GenerationStep.AUDIO_SYNTHESIZE,
                        message=f"音频 {index+1}/{total} 合成失败",
                        error=e,
                        input_params={"text": text, "voice_id": voice_id, "page_index": index + 1},
                    )
                raise

            if on_progress:
                on_progress(GenerationProgress("audio", index + 1, total, f"音频 {index + 1}/{total} 完成"))

            return result
