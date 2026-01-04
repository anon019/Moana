# src/moana/services/video/minimax.py
"""MiniMax (Hailuo) 视频生成服务."""
import asyncio
import logging
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type

from moana.config import get_settings
from moana.services.video.base import BaseVideoService, VideoResult
from moana.services.storage import get_storage_service

logger = logging.getLogger(__name__)


class VideoServiceError(Exception):
    """视频服务错误基类."""
    pass


class InsufficientBalanceError(VideoServiceError):
    """余额不足错误（不应重试）."""
    pass


class MiniMaxVideoService(BaseVideoService):
    """MiniMax Hailuo 视频生成服务实现.

    使用 MiniMax video_generation API 从图片生成视频。
    支持 video-01 和 Hailuo-2.3-Fast 模型。
    """

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.minimax_api_key
        self._api_base = settings.minimax_api_base
        self._model = settings.minimax_video_model

    @property
    def provider_name(self) -> str:
        return "minimax"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type(InsufficientBalanceError),  # 余额不足不重试
    )
    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int | None = None,
        last_frame_url: str | None = None,
        # New parameters for interface compatibility (ignored by MiniMax)
        scene_template: str | None = None,
        character_ids: list[str] | None = None,
        reference_images: list[str] | None = None,
        auto_enhance_prompt: bool = True,
        negative_prompt: str | None = None,
    ) -> VideoResult:
        """从图片生成视频.

        Args:
            image_url: 图片 URL（作为视频首帧）
            prompt: 视频描述文本
            duration_seconds: 视频时长（秒），MiniMax 默认 6 秒
            last_frame_url: Ignored by MiniMax
            scene_template: Ignored by MiniMax
            character_ids: Ignored by MiniMax
            reference_images: Ignored by MiniMax
            auto_enhance_prompt: Ignored by MiniMax
            negative_prompt: Ignored by MiniMax

        Returns:
            VideoResult 包含生成的视频信息

        Note: Veo-specific enhancement parameters are accepted for interface
        compatibility but not used by MiniMax.
        """
        # Log if Veo-specific features are requested
        if reference_images or character_ids:
            logger.warning("Reference images not supported by MiniMax, ignoring")
        # Step 1: 创建视频生成任务
        task_id = await self._create_task(image_url, prompt)

        # Step 2: 轮询等待任务完成
        result = await self._wait_for_completion(task_id)

        return result

    async def _create_task(self, image_url: str, prompt: str) -> str:
        """创建视频生成任务."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/video_generation",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "first_frame_image": image_url,
                },
            )
            response.raise_for_status()
            result = response.json()

        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            error_msg = base_resp.get("status_msg", "Unknown error")
            # 检查是否是余额不足错误
            if "insufficient balance" in error_msg.lower():
                raise InsufficientBalanceError(
                    "MiniMax 账户余额不足，请前往 https://platform.minimaxi.com 充值"
                )
            raise RuntimeError(f"Video generation failed: {error_msg}")

        task_id = result.get("task_id")
        if not task_id:
            raise RuntimeError("No task_id in response")

        return task_id

    async def _wait_for_completion(
        self,
        task_id: str,
        max_wait_seconds: int = 600,  # 最多等待 10 分钟
        poll_interval: int = 10,  # 每 10 秒查询一次
    ) -> VideoResult:
        """轮询等待任务完成."""
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(f"Video generation timed out after {max_wait_seconds}s")

            # 查询任务状态
            status, result = await self._query_task(task_id)

            if status == "Success":
                # 任务完成，解析结果
                file_id = result.get("file_id")
                remote_url = await self._get_video_url(file_id) if file_id else ""

                # 下载视频并保存到本地存储
                local_url = await self._download_and_save(remote_url)

                return VideoResult(
                    video_url=local_url,
                    duration=6.0,  # MiniMax 默认 6 秒
                    thumbnail_url="",  # MiniMax 不返回缩略图
                    model=self._model,
                    resolution="720P",
                    has_audio=False,
                )
            elif status == "Fail":
                raise RuntimeError(f"Video generation failed: {result}")
            elif status in ("Queueing", "Processing", "Preparing"):
                # 继续等待
                await asyncio.sleep(poll_interval)
            else:
                raise RuntimeError(f"Unknown status: {status}")

    async def _query_task(self, task_id: str) -> tuple[str, dict]:
        """查询任务状态."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._api_base}/v1/query/video_generation",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
                params={"task_id": task_id},
            )
            response.raise_for_status()
            result = response.json()

        status = result.get("status", "Unknown")
        return status, result

    async def _get_video_url(self, file_id: str) -> str:
        """获取视频下载 URL."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._api_base}/v1/files/retrieve",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                },
                params={"file_id": file_id},
            )
            response.raise_for_status()
            result = response.json()

        file_info = result.get("file", {})
        return file_info.get("download_url", "")

    async def _download_and_save(self, remote_url: str) -> str:
        """下载视频并保存到本地存储.

        Args:
            remote_url: MiniMax 返回的临时视频 URL

        Returns:
            本地存储的公开 URL
        """
        if not remote_url:
            raise RuntimeError("No video URL to download")

        logger.info(f"Downloading video from MiniMax...")

        # 下载视频
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(remote_url)
            response.raise_for_status()
            video_data = response.content

        logger.info(f"Downloaded {len(video_data)} bytes, saving to local storage...")

        # 保存到本地存储
        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=video_data,
            key="video.mp4",  # 会被自动重命名为 video/{date}/{hash}.mp4
            content_type="video/mp4",
        )

        if not result.success:
            raise RuntimeError(f"Failed to save video: {result.error}")

        logger.info(f"Video saved to: {result.url}")
        return result.url
