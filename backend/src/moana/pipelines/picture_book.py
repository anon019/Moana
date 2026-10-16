import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import logging
from pydantic import BaseModel, Field, ConfigDict

# Python 3.6 compatibility: asynccontextmanager was added in 3.7
try:
    from contextlib import asynccontextmanager
except ImportError:
    # Backport for Python 3.6
    from functools import wraps

    def asynccontextmanager(func):
        """Decorator for async context managers (Python 3.6 compatible)."""
        @wraps(func)
        async def helper(*args, **kwargs):
            return _AsyncContextManager(func(*args, **kwargs))
        return helper

    class _AsyncContextManager:
        """Async context manager wrapper for Python 3.6."""
        def __init__(self, gen):
            self._gen = gen

        async def __aenter__(self):
            return await self._gen.asend(None)

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            try:
                if exc_type is None:
                    await self._gen.asend(None)
                else:
                    await self._gen.athrow(exc_type, exc_val, exc_tb)
            except StopAsyncIteration:
                return False
            except:
                if exc_type is not None:
                    return False
                raise

from moana.agents.story import StoryAgent, StyleConfig, StoryEnhancement, VisualEnhancement
from moana.services.image import get_image_service
from moana.services.image.base import BaseImageService, ImageStyle
from moana.services.tts import get_tts_service
from moana.services.tts.base import BaseTTSService
from moana.services.logging import GenerationLogger
from moana.models.generation_log import GenerationStep
from moana.styles import get_default_color

logger = logging.getLogger(__name__)
_PICTURE_BOOK_GENERATION_LOCK = asyncio.Lock()



class ProtagonistConfig(BaseModel):
    """Configuration for the story protagonist."""
    animal: str = Field(default="bunny", description="主角动物 (bunny, bear, cat, dog, panda, fox, elephant, monkey, penguin)")
    color: str | None = Field(default=None, description="主角颜色 (white, brown, orange 等)，为 None 时按动物类型自动选择")
    accessory: str | None = Field(default=None, description="主角配饰 (blue overalls, red scarf 等)，为 None 时由大模型自由创作")


class StoryEnhancementConfig(BaseModel):
    """Story enhancement configuration."""
    narrative_pace: Optional[str] = Field(default=None, description="叙事节奏")
    interaction_density: Optional[str] = Field(default=None, description="互动密度")
    educational_focus: Optional[str] = Field(default=None, description="教育侧重")
    language_style: Optional[str] = Field(default=None, description="语言风格")
    plot_complexity: Optional[str] = Field(default=None, description="情节复杂度")
    ending_style: Optional[str] = Field(default=None, description="结局风格")


class VisualEnhancementConfig(BaseModel):
    """Visual enhancement configuration."""
    time_atmosphere: Optional[str] = Field(default=None, description="时间氛围")
    scene_environment: Optional[str] = Field(default=None, description="场景环境")
    emotional_tone: Optional[str] = Field(default=None, description="情感基调")
    composition_style: Optional[str] = Field(default=None, description="构图风格")
    lighting_effect: Optional[str] = Field(default=None, description="光影效果")


class GenerationRequest(BaseModel):
    """Request object encapsulating all parameters for picture book generation.

    This consolidates the 17+ parameters of the generate() method into a single
    structured object for cleaner APIs and easier parameter passing.
    """
    # Required child/theme parameters
    child_name: str = Field(description="孩子名字")
    age_months: int = Field(description="孩子月龄")
    theme_topic: str = Field(description="主题")
    theme_category: str = Field(description="类别")

    # Optional personalization
    favorite_characters: Optional[list[str]] = Field(default=None, description="喜欢的角色")
    voice_id: Optional[str] = Field(default=None, description="TTS 声音ID")

    # Art style parameters
    art_style: str = Field(default="pixar_3d", description="美术风格 (pixar_3d, watercolor, flat_vector, crayon, anime)")
    color_palette: str = Field(default="pastel", description="色彩风格 (pastel, vibrant, warm, cool, monochrome)")

    # Protagonist configuration
    protagonist: Optional[ProtagonistConfig] = Field(default=None, description="主角设定")

    # Enhancement configurations
    story_enhancement: Optional[StoryEnhancementConfig] = Field(default=None, description="故事增强配置")
    visual_enhancement: Optional[VisualEnhancementConfig] = Field(default=None, description="视觉增强配置")

    # Progress callback (excluded from serialization)
    on_progress: Optional[Callable[["GenerationProgress"], None]] = Field(default=None, exclude=True)

    # Task tracking
    task_id: Optional[str] = Field(default=None, description="任务 ID，用于日志记录")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_legacy_params(
        cls,
        child_name: str,
        age_months: int,
        theme_topic: str,
        theme_category: str,
        favorite_characters: Optional[list[str]] = None,
        voice_id: Optional[str] = None,
        on_progress: Optional[Callable] = None,
        art_style: Optional[str] = None,
        protagonist_animal: Optional[str] = None,
        protagonist_color: Optional[str] = None,
        protagonist_accessory: Optional[str] = None,
        color_palette: Optional[str] = None,
        story_enhancement: Optional[dict] = None,
        visual_enhancement: Optional[dict] = None,
        task_id: Optional[str] = None,
    ) -> "GenerationRequest":
        """Create a GenerationRequest from legacy individual parameters.

        This factory method provides backward compatibility with code that
        still passes individual parameters.
        """
        # Build protagonist config if any protagonist param is provided
        protagonist = None
        if protagonist_animal or protagonist_color or protagonist_accessory:
            protagonist = ProtagonistConfig(
                animal=protagonist_animal or "bunny",
                color=protagonist_color,  # None 时由 _build_style_config 按动物类型决定
                accessory=protagonist_accessory,
            )

        # Build story enhancement config if provided
        story_enh = None
        if story_enhancement:
            story_enh = StoryEnhancementConfig(**story_enhancement)

        # Build visual enhancement config if provided
        visual_enh = None
        if visual_enhancement:
            visual_enh = VisualEnhancementConfig(**visual_enhancement)

        return cls(
            child_name=child_name,
            age_months=age_months,
            theme_topic=theme_topic,
            theme_category=theme_category,
            favorite_characters=favorite_characters,
            voice_id=voice_id,
            art_style=art_style or "pixar_3d",
            color_palette=color_palette or "pastel",
            protagonist=protagonist,
            story_enhancement=story_enh,
            visual_enhancement=visual_enh,
            on_progress=on_progress,
            task_id=task_id,
        )

    def to_style_config(self) -> StyleConfig:
        """Convert request parameters to StyleConfig for StoryAgent."""
        # Build StoryEnhancement from config
        story_enh = None
        if self.story_enhancement:
            story_enh = StoryEnhancement(
                narrative_pace=self.story_enhancement.narrative_pace,
                interaction_density=self.story_enhancement.interaction_density,
                educational_focus=self.story_enhancement.educational_focus,
                language_style=self.story_enhancement.language_style,
                plot_complexity=self.story_enhancement.plot_complexity,
                ending_style=self.story_enhancement.ending_style,
            )

        # Build VisualEnhancement from config
        visual_enh = None
        if self.visual_enhancement:
            visual_enh = VisualEnhancement(
                time_atmosphere=self.visual_enhancement.time_atmosphere,
                scene_environment=self.visual_enhancement.scene_environment,
                emotional_tone=self.visual_enhancement.emotional_tone,
                composition_style=self.visual_enhancement.composition_style,
                lighting_effect=self.visual_enhancement.lighting_effect,
            )

        # Get protagonist values
        protagonist = self.protagonist or ProtagonistConfig()

        # 根据动物类型决定默认颜色，避免所有动物都 fallback 到 white
        color = protagonist.color or get_default_color(protagonist.animal)

        return StyleConfig(
            art_style=self.art_style,
            protagonist_animal=protagonist.animal,
            protagonist_color=color,
            protagonist_accessory=protagonist.accessory,
            color_palette=self.color_palette,
            story_enhancement=story_enh,
            visual_enhancement=visual_enh,
        )


@asynccontextmanager
async def logged_step(
    gen_logger: Optional[GenerationLogger],
    step: GenerationStep,
    message: str,
    input_params: Optional[dict] = None,
):
    """Context manager for logging generation steps with timing.

    Usage:
        async with logged_step(logger, GenerationStep.STORY_GENERATE, "Generating story"):
            result = await some_operation()

    This automatically:
    - Records start time
    - Logs success with duration on normal exit
    - Logs error with details on exception
    """
    start_time = time.time()
    result_holder = {"output": None, "message": message}

    try:
        yield result_holder
        duration = time.time() - start_time

        if gen_logger:
            await gen_logger.log_step(
                step=step,
                message=result_holder.get("message", message),
                input_params=input_params,
                output_result=result_holder.get("output"),
                duration=duration,
            )
    except Exception as e:
        if gen_logger:
            await gen_logger.log_error(
                step=step,
                message=f"{message} 失败",
                error=e,
                input_params=input_params,
            )
        raise


@dataclass
class GenerationProgress:
    """Progress tracking for generation."""
    stage: str
    current: int
    total: int
    message: str


class PictureBookPipeline:
    """Pipeline for generating complete picture books."""

    # 每本书一次只处理一个媒体请求。
    TTS_CONCURRENCY_LIMIT = 1
    IMAGE_CONCURRENCY_LIMIT = 1

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
        request: GenerationRequest | None = None,
        # Legacy parameters for backward compatibility
        child_name: str | None = None,
        age_months: int | None = None,
        theme_topic: str | None = None,
        theme_category: str | None = None,
        favorite_characters: list[str] | None = None,
        voice_id: str | None = None,
        on_progress: Callable[[GenerationProgress], None] | None = None,
        art_style: str | None = None,
        protagonist_animal: str | None = None,
        protagonist_color: str | None = None,
        protagonist_accessory: str | None = None,
        color_palette: str | None = None,
        story_enhancement: dict | None = None,
        visual_enhancement: dict | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a complete picture book with images and audio.

        This method supports two calling conventions:

        1. New style with GenerationRequest object:
            await pipeline.generate(request=GenerationRequest(...))

        2. Legacy style with individual parameters (for backward compatibility):
            await pipeline.generate(
                child_name="小明",
                age_months=24,
                theme_topic="刷牙",
                theme_category="habit",
                ...
            )

        Args:
            request: GenerationRequest object encapsulating all parameters (preferred)
            child_name: 孩子名字 (legacy)
            age_months: 孩子月龄 (legacy)
            theme_topic: 主题 (legacy)
            theme_category: 类别 (legacy)
            favorite_characters: 喜欢的角色 (legacy)
            voice_id: TTS 声音ID (legacy)
            on_progress: 进度回调 (legacy)
            art_style: 美术风格 (legacy)
            protagonist_animal: 主角动物 (legacy)
            protagonist_color: 主角颜色 (legacy)
            protagonist_accessory: 主角配饰 (legacy)
            color_palette: 色彩风格 (legacy)
            story_enhancement: 故事增强配置 (legacy)
            visual_enhancement: 视觉增强配置 (legacy)
            task_id: 任务 ID (legacy)

        Returns:
            dict containing the complete picture book data
        """
        # Normalize to GenerationRequest
        if request is None:
            if child_name is None or age_months is None or theme_topic is None or theme_category is None:
                raise ValueError(
                    "Either 'request' must be provided, or all of "
                    "'child_name', 'age_months', 'theme_topic', 'theme_category' must be specified"
                )
            request = GenerationRequest.from_legacy_params(
                child_name=child_name,
                age_months=age_months,
                theme_topic=theme_topic,
                theme_category=theme_category,
                favorite_characters=favorite_characters,
                voice_id=voice_id,
                on_progress=on_progress,
                art_style=art_style,
                protagonist_animal=protagonist_animal,
                protagonist_color=protagonist_color,
                protagonist_accessory=protagonist_accessory,
                color_palette=color_palette,
                story_enhancement=story_enhancement,
                visual_enhancement=visual_enhancement,
                task_id=task_id,
            )
        else:
            # Override on_progress if passed separately (common pattern for callbacks)
            if on_progress is not None:
                request.on_progress = on_progress

        # 所有 API 入口共享此锁，避免不同请求各自创建一条并行绘本管线。
        async with _PICTURE_BOOK_GENERATION_LOCK:
            validator = getattr(self._tts_service, "validate_configuration", None)
            if validator is not None:
                validator(request.voice_id)
            return await self._generate_from_request(request)

    async def _generate_from_request(self, request: GenerationRequest) -> dict[str, Any]:
        """Internal implementation that generates from a GenerationRequest.

        This is the core generation logic, separated for cleaner code organization.
        """
        # Initialize logger
        gen_logger = GenerationLogger(task_id=request.task_id) if request.task_id else None

        # Build style config from request
        style_config = request.to_style_config()

        # Extract commonly used values
        on_progress = request.on_progress

        # Log initialization
        if gen_logger:
            await gen_logger.log_step(
                step=GenerationStep.INIT,
                message="开始生成绘本",
                input_params={
                    "child_name": request.child_name,
                    "age_months": request.age_months,
                    "theme_topic": request.theme_topic,
                    "theme_category": request.theme_category,
                    "art_style": request.art_style,
                    "protagonist": request.protagonist.model_dump() if request.protagonist else None,
                    "color_palette": request.color_palette,
                },
            )

        # Stage 1: Generate story outline
        if on_progress:
            on_progress(GenerationProgress("outline", 0, 1, "正在创作故事..."))

        async with logged_step(
            gen_logger,
            GenerationStep.STORY_GENERATE,
            "故事大纲生成",
            input_params={"style_config": style_config.__dict__ if hasattr(style_config, '__dict__') else str(style_config)},
        ) as step_result:
            outline = await self._story_agent.generate_outline(
                child_name=request.child_name,
                age_months=request.age_months,
                theme_topic=request.theme_topic,
                theme_category=request.theme_category,
                favorite_characters=request.favorite_characters,
                style_config=style_config,
            )
            step_result["message"] = f"故事大纲生成完成: {outline.title}"
            step_result["output"] = {
                "title": outline.title,
                "page_count": len(outline.pages),
                "educational_goal": outline.educational_goal,
            }

        if on_progress:
            on_progress(GenerationProgress("outline", 1, 1, "故事创作完成"))

        # Stage 2: Generate images one page at a time.
        if on_progress:
            on_progress(GenerationProgress("images", 0, len(outline.pages), "正在生成插图..."))

        # 角色一致性保障：构建主角描述标签，确保每张图都包含
        protagonist_tag = self._build_protagonist_tag(style_config)

        async with logged_step(
            gen_logger,
            GenerationStep.IMAGE_GENERATE,
            f"逐张图片生成 ({len(outline.pages)} 张)",
        ) as step_result:
            image_results = []
            for idx, page in enumerate(outline.pages):
                prompt = self._ensure_protagonist_in_prompt(page.image_prompt, protagonist_tag)
                try:
                    result = await self._generate_page_image(
                        prompt, idx, len(outline.pages), on_progress, gen_logger,
                    )
                except Exception:
                    logger.warning(f"[PictureBook] Image {idx+1} failed, retrying once...")
                    try:
                        await asyncio.sleep(3)
                        result = await self._generate_page_image(
                            prompt, idx, len(outline.pages), on_progress, gen_logger,
                        )
                    except Exception as error:
                        logger.error(f"[PictureBook] Image {idx+1} retry failed, will save partial: {error}")
                        result = error
                image_results.append(result)

            success_count = sum(1 for r in image_results if not isinstance(r, BaseException))
            step_result["message"] = f"图片生成完成 ({success_count}/{len(image_results)} 张)"
            step_result["output"] = {
                "image_count": success_count,
                "failed_count": len(image_results) - success_count,
            }

        # Stage 3: Generate audio one page at a time, after all images.
        if on_progress:
            on_progress(GenerationProgress("audio", 0, len(outline.pages), "正在生成朗读音频..."))

        async with logged_step(
            gen_logger,
            GenerationStep.AUDIO_SYNTHESIZE,
            f"逐条音频合成 ({len(outline.pages)} 条)",
        ) as step_result:
            audio_results = []
            for idx, page in enumerate(outline.pages):
                try:
                    result = await self._generate_page_audio(
                        page.text, request.voice_id, idx, len(outline.pages), on_progress, gen_logger,
                    )
                except Exception as error:
                    # 保留部分稿件，不自动回退 Google 或其他付费 TTS。
                    logger.error("[PictureBook] 音频 %s 合成失败，保留稿件: %s", idx + 1, type(error).__name__)
                    result = error
                audio_results.append(result)

            success_count = sum(1 for r in audio_results if not isinstance(r, BaseException))
            step_result["message"] = f"音频生成完成 ({success_count}/{len(audio_results)} 条)"
            step_result["output"] = {
                "audio_count": success_count,
                "failed_count": len(audio_results) - success_count,
            }

        # Combine results (tolerant of partial failures)
        pages = []
        total_duration = 0
        failed_pages = []

        for i, page in enumerate(outline.pages):
            img_result = image_results[i]
            audio_result = audio_results[i]
            img_ok = not isinstance(img_result, BaseException)
            audio_ok = not isinstance(audio_result, BaseException)

            page_data = {
                "page_num": page.page_num,
                "text": page.text,
                "image_url": img_result.url if img_ok else "",
                "image_thumb_url": img_result.thumb_url if img_ok else "",
                "image_prompt": page.image_prompt,
                "audio_url": audio_result.audio_url if audio_ok else "",
                "audio_duration": audio_result.duration if audio_ok else 0,
                "audio_model": audio_result.model if audio_ok else None,
                "audio_voice_id": audio_result.voice_id if audio_ok else None,
                "image_model": img_result.model if img_ok else None,
                "interaction": page.interaction.model_dump() if page.interaction else None,
            }
            pages.append(page_data)
            if audio_ok:
                total_duration += audio_result.duration
            if not img_ok or not audio_ok:
                failed_pages.append({
                    "page_num": page.page_num,
                    "image_failed": not img_ok,
                    "audio_failed": not audio_ok,
                    "image_error": str(img_result) if not img_ok else None,
                    "audio_error": str(audio_result) if not audio_ok else None,
                })

        if failed_pages:
            logger.warning(f"[PictureBook] Saving with {len(failed_pages)} incomplete page(s): {failed_pages}")

        return {
            "title": outline.title,
            "theme_topic": outline.theme_topic,
            "educational_goal": outline.educational_goal,
            "pages": pages,
            "total_duration": total_duration,
            "failed_pages": failed_pages,
            "total_interactions": outline.total_interactions,
            "personalization": {
                "child_name": request.child_name,
                "favorite_characters": request.favorite_characters or [],
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
                "requested_image_model": getattr(self._image_service, 'requested_model', None),
                "image_tool": "codex_cli" if getattr(self._image_service, 'provider_name', None) == "codex" else None,
                "tts_model": getattr(self._tts_service, 'model_name', 'unknown'),
                "tts_voice_id": next((r.voice_id for r in audio_results if not isinstance(r, BaseException)), None),
            },
        }

    @staticmethod
    def _build_protagonist_tag(style_config) -> str:
        """根据风格配置构建主角描述标签，用于一致性注入.

        复用 story.py 中的公共函数，避免逻辑重复导致描述漂移。
        延迟导入是为了避免与 story.py 的循环依赖。
        """
        from moana.agents.story import build_protagonist_desc
        return build_protagonist_desc(style_config)

    @staticmethod
    def _ensure_protagonist_in_prompt(prompt: str, protagonist_tag: str) -> str:
        """确保 image_prompt 中包含完整的主角描述.

        使用精确子串匹配：如果 LLM 遵从了"逐字复制"指令，
        prompt 中会包含完整的 protagonist_tag；如果不包含，
        则在风格描述词之后自动注入，保障角色一致性。
        """
        if protagonist_tag.lower() in prompt.lower():
            return prompt

        # 未找到完整主角描述，在第一个逗号后注入
        comma_idx = prompt.find(",")
        if comma_idx > 0:
            rest = prompt[comma_idx + 1:].lstrip()
            return f"{prompt[:comma_idx]}, {protagonist_tag}, {rest}"
        else:
            return f"{protagonist_tag}, {prompt}"

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
            # 短暂让出事件循环，避免饥饿
            await asyncio.sleep(0.1)

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

    async def _retry_audio_with_fallback(self, *args, **kwargs):
        """兼容旧调用；免费语音失败时禁止自动切换付费后端。"""
        raise RuntimeError("语音合成失败；自动付费回退已禁用，请检查配置的 CLI 后端")
