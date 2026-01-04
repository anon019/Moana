"""Google Veo 3.1 video generation service - Enhanced."""
import asyncio
import logging

import httpx
from google import genai
from google.genai import types

from moana.config import get_settings
from moana.services.storage import get_storage_service
from moana.services.video.base import BaseVideoService, VideoResult
from moana.services.video.templates import get_template, get_default_template
from moana.services.video.prompt_enhancer import VeoPromptEnhancer
from moana.services.video.reference_manager import ReferenceImageManager

logger = logging.getLogger(__name__)


class VeoServiceError(Exception):
    """Base error for Veo service."""
    pass


class GoogleVeoService(BaseVideoService):
    """Enhanced Google Veo 3.1 video generation service."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.google_api_key
        self._model = settings.veo_model
        self._resolution = settings.veo_resolution
        self._default_duration = settings.veo_duration
        self._client = genai.Client(api_key=self._api_key)

        # Enhancement systems
        self._prompt_enhancer = VeoPromptEnhancer()
        self._reference_manager = ReferenceImageManager()

    @property
    def provider_name(self) -> str:
        return "veo"

    @property
    def reference_manager(self) -> ReferenceImageManager:
        """Access the reference manager for character registration."""
        return self._reference_manager

    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int = 5,
        last_frame_url: str | None = None,
        scene_template: str | None = None,
        character_ids: list[str] | None = None,
        reference_images: list[str] | None = None,
        auto_enhance_prompt: bool = True,
        negative_prompt: str | None = None,
    ) -> VideoResult:
        """Generate video using enhanced Veo 3.1 API.

        Args:
            image_url: Start image URL (first frame)
            prompt: Video description
            duration_seconds: Video duration (max 8s for Veo)
            last_frame_url: End image URL (optional)
            scene_template: Template ID for preset parameters
            character_ids: Character IDs for reference images
            reference_images: Direct reference image URLs
            auto_enhance_prompt: Auto-enhance the prompt
            negative_prompt: Custom negative prompt

        Returns:
            VideoResult with generated video info
        """
        # 1. Load template or use defaults
        template = get_template(scene_template) if scene_template else get_default_template()

        # 2. Determine parameters (user override > template > default)
        # Veo 3.1 要求 duration 在 4-8 秒范围内
        duration = max(4, min(duration_seconds or template.duration, 8))
        resolution = template.resolution

        logger.info(f"Generating video with Veo 3.1 [template={scene_template}, duration={duration}s]")

        # 3. Enhance prompt if enabled
        final_prompt = prompt
        final_negative = negative_prompt or template.negative_prompt

        if auto_enhance_prompt:
            try:
                enhanced = await self._prompt_enhancer.enhance(
                    prompt=prompt,
                    use_llm=True,
                    motion_mode=template.motion_mode,
                    template_camera_prompt=template.camera_prompt,
                )
                final_prompt = enhanced.enhanced_prompt
                final_negative = enhanced.negative_prompt
                logger.info(f"Prompt enhanced: {final_prompt[:100]}...")
            except Exception as e:
                logger.warning(f"Prompt enhancement failed, using original: {e}")

        # 4. Collect reference images
        refs: list[str] = []
        if reference_images:
            refs = reference_images[:3]
        elif character_ids:
            refs = self._reference_manager.get_references_for_scene(character_ids)

        # 5. Download and prepare images
        image_bytes = await self._download_image(image_url)
        mime_type = "image/png" if image_url.endswith(".png") else "image/jpeg"
        start_image = types.Image(imageBytes=image_bytes, mimeType=mime_type)

        # 6. Build config
        # Note: generate_audio is not supported in current Gemini API version
        # Veo 3.1 may generate audio by default or this feature is not yet available
        config = types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=duration,
            negative_prompt=final_negative,
        )

        # Add last_frame if provided
        if last_frame_url:
            logger.info("Using last_frame for video generation")
            last_frame_bytes = await self._download_image(last_frame_url)
            last_mime_type = "image/png" if last_frame_url.endswith(".png") else "image/jpeg"
            config.last_frame = types.Image(imageBytes=last_frame_bytes, mimeType=last_mime_type)

        # 7. Prepare reference images if any
        ref_images = None
        if refs:
            logger.info(f"Using {len(refs)} reference images")
            ref_images = []
            for ref_url in refs:
                ref_bytes = await self._download_image(ref_url)
                ref_mime = "image/png" if ref_url.endswith(".png") else "image/jpeg"
                ref_images.append(types.Image(imageBytes=ref_bytes, mimeType=ref_mime))

        # 8. Submit video generation
        generate_kwargs = {
            "model": self._model,
            "prompt": final_prompt,
            "image": start_image,
            "config": config,
        }
        if ref_images:
            generate_kwargs["reference_images"] = ref_images

        operation = self._client.models.generate_videos(**generate_kwargs)
        logger.info(f"Veo task submitted: {operation.name}")

        # 9. Poll until complete
        operation = await self._poll_until_complete(operation, timeout=600, interval=10)

        # 10. Download and save
        if not operation.response or not operation.response.generated_videos:
            raise VeoServiceError("No video in Veo response")

        video = operation.response.generated_videos[0]
        local_url = await self._download_and_save_video(video)

        return VideoResult(
            video_url=local_url,
            duration=duration,
            thumbnail_url=image_url,
            model=self._model,
            resolution=resolution,
            format="mp4",
            has_audio=False,  # Audio generation not yet supported in current API
        )

    async def _download_image(self, image_url: str) -> bytes:
        """Download image from URL or read from local storage.

        如果 URL 是本地存储的图片，直接读取本地文件避免网络问题。
        """
        # 检查是否是本地存储的图片
        local_base_url = "https://example.com/media/"
        local_storage_path = "/var/www/kids/media/"

        if image_url.startswith(local_base_url):
            # 转换为本地路径
            relative_path = image_url.replace(local_base_url, "")
            local_path = local_storage_path + relative_path

            logger.info(f"Reading local image: {local_path}")
            try:
                with open(local_path, "rb") as f:
                    return f.read()
            except FileNotFoundError:
                logger.warning(f"Local file not found, falling back to HTTP: {local_path}")

        # 回退到 HTTP 下载
        logger.info(f"Downloading image from URL: {image_url}")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return response.content

    async def _poll_until_complete(self, operation, timeout: int = 600, interval: int = 10):
        """Poll Veo API until operation completes."""
        elapsed = 0

        while elapsed < timeout:
            if operation.done:
                logger.info("Veo operation completed")
                return operation

            logger.debug(f"Veo operation in progress, waiting {interval}s...")
            await asyncio.sleep(interval)
            elapsed += interval

            # Refresh operation status
            operation = self._client.operations.get(operation)

        raise VeoServiceError(f"Veo operation timed out after {timeout}s")

    async def _download_and_save_video(self, generated_video) -> str:
        """Download video and save to local storage."""
        logger.info("Downloading video from Veo...")

        # Get the Video object from GeneratedVideo
        video = generated_video.video

        # Download video bytes if not already loaded
        if video.video_bytes:
            video_data = video.video_bytes
        elif video.uri:
            # Download from URI
            self._client.files.download(file=video)
            video_data = video.video_bytes
        else:
            raise VeoServiceError("No video data available")

        logger.info(f"Downloaded {len(video_data)} bytes, saving to local storage...")

        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=video_data,
            key="video.mp4",
            content_type="video/mp4",
        )

        if not result.success:
            raise VeoServiceError(f"Failed to save video: {result.error}")

        logger.info(f"Video saved to: {result.url}")
        return result.url
