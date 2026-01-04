# src/moana/services/video/wanx.py
"""阿里万相视频生成服务 (Wanx Video Service).

支持模型:
- wan2.6-i2v: 最新有声版，支持多镜头叙事，720P/1080P，5/10/15秒

API 文档: https://help.aliyun.com/zh/model-studio/image-to-video-api-reference

注意: 使用 HTTP API 直接调用，绕过 DashScope SDK 以避免网络问题。
图片会先压缩后转为 base64 传递，解决阿里云访问 Cloudflare 超时的问题。
"""
import asyncio
import base64
import hashlib
import time
from io import BytesIO

import httpx
from PIL import Image

from moana.config import get_settings
from moana.services.video.base import BaseVideoService, VideoResult
from moana.services.storage import get_storage_service


class WanxVideoService(BaseVideoService):
    """阿里万相 Wan2.6 视频生成服务实现.

    使用 HTTP API 直接调用万相 I2V (图生视频) API。
    """

    # API 端点
    API_BASE = "https://dashscope.aliyuncs.com/api/v1"
    SUBMIT_ENDPOINT = f"{API_BASE}/services/aigc/video-generation/video-synthesis"
    TASK_ENDPOINT = f"{API_BASE}/tasks"

    # 可用模型
    MODELS = {
        "wan2.6-i2v": {
            "description": "最新有声版，支持多镜头叙事",
            "resolutions": ["720P", "1080P"],
            "durations": [5, 10, 15],
            "has_audio": True,
        },
    }

    def __init__(self, model: str | None = None):
        settings = get_settings()
        self._api_key = settings.dashscope_api_key
        self._model = model or settings.wanx_video_model
        self._default_resolution = "720P"
        self._default_duration = settings.wanx_video_duration

    @property
    def provider_name(self) -> str:
        return "wanx"

    @classmethod
    def get_video_options(cls) -> dict:
        """获取视频生成选项（供 API 返回给前端）."""
        return {
            "models": [
                {
                    "id": model_id,
                    "description": info["description"],
                    "resolutions": info["resolutions"],
                    "durations": info["durations"],
                    "has_audio": info["has_audio"],
                    "recommended": model_id == "wan2.6-i2v",
                }
                for model_id, info in cls.MODELS.items()
            ],
            "resolutions": [
                {"id": "720P", "name": "720P 高清"},
                {"id": "1080P", "name": "1080P 全高清"},
            ],
            "durations": [
                {"value": 5, "label": "5秒"},
                {"value": 10, "label": "10秒"},
                {"value": 15, "label": "15秒"},
            ],
        }

    async def _convert_image_to_base64(self, image_url: str, max_retries: int = 3) -> str:
        """将图片 URL 转换为压缩的 base64 编码.

        包含重试逻辑以应对网络不稳定。
        """
        if image_url.startswith("data:"):
            return image_url

        # 下载图片（带重试）
        image_data = None
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image_data = response.content

                    # 验证下载完整性
                    content_length = response.headers.get("content-length")
                    if content_length and len(image_data) < int(content_length):
                        raise ValueError(
                            f"Incomplete download: got {len(image_data)}, expected {content_length}"
                        )

                    print(f"[Wanx] 图片下载成功 ({len(image_data)/1024:.1f} KB)")
                    break

            except Exception as e:
                last_error = e
                print(f"[Wanx] 图片下载失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避

        if image_data is None:
            raise RuntimeError(f"Failed to download image after {max_retries} attempts: {last_error}")

        # 压缩图片
        try:
            img = Image.open(BytesIO(image_data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 缩放到 1280 最大边
            max_size = 1280
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 转换为 JPEG
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            compressed_data = buffer.getvalue()

            b64_data = base64.b64encode(compressed_data).decode("utf-8")
            return f"data:image/jpeg;base64,{b64_data}"

        except Exception as e:
            print(f"[Wanx] 图片压缩失败: {e}")
            raise

    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int | None = None,
        last_frame_url: str | None = None,
        # New parameters for interface compatibility (mostly ignored by Wanx)
        scene_template: str | None = None,
        character_ids: list[str] | None = None,
        reference_images: list[str] | None = None,
        auto_enhance_prompt: bool = True,
        negative_prompt: str | None = None,
        # Wanx-specific parameters
        resolution: str | None = None,
        shot_type: str | None = None,
        enable_audio: bool = True,
        audio_url: str | None = None,
    ) -> VideoResult:
        """从图片生成视频.

        Note: Veo-specific parameters (scene_template, character_ids, reference_images,
        negative_prompt) are accepted for interface compatibility but not used by Wanx.
        """
        # Log if Veo-specific features are requested
        if reference_images or character_ids:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Reference images not supported by Wanx, ignoring")
        if scene_template:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Scene template '{scene_template}' specified - Wanx will use duration parameter only")
        duration = duration_seconds or self._default_duration
        res = resolution or self._default_resolution

        # 验证参数
        model_info = self.MODELS.get(self._model, self.MODELS["wan2.6-i2v"])
        if res not in model_info["resolutions"]:
            res = model_info["resolutions"][0]
        if duration not in model_info["durations"]:
            duration = model_info["durations"][0]

        try:
            # 转换图片为 base64
            print(f"[Wanx] 正在下载并压缩图片: {image_url}")
            image_data = await self._convert_image_to_base64(image_url)
            print(f"[Wanx] 图片压缩完成 ({len(image_data)/1024:.1f} KB)")

            # 提交任务
            print(f"[Wanx] 提交视频生成任务...")
            task_id = await self._submit_task(
                image_data, prompt, duration, res, enable_audio
            )
            print(f"[Wanx] 任务已提交: {task_id}")

            # 等待任务完成
            print(f"[Wanx] 等待视频生成（预计 2-3 分钟）...")
            video_url = await self._wait_for_task(task_id)
            print(f"[Wanx] 视频生成完成: {video_url[:80]}...")

            # 保存到本地存储
            print(f"[Wanx] 保存视频到本地存储...")
            local_url = await self._save_to_local_storage(video_url, prompt)
            print(f"[Wanx] 视频保存成功: {local_url}")

            return VideoResult(
                video_url=local_url,
                duration=float(duration),
                thumbnail_url=image_url,
                model=self._model,
                resolution=res,
                has_audio=model_info.get("has_audio", False),
            )

        except Exception as e:
            print(f"[Wanx] 视频生成失败: {type(e).__name__}: {e}")
            raise

    async def _submit_task(
        self,
        image_data: str,
        prompt: str,
        duration: int,
        resolution: str,
        enable_audio: bool,
    ) -> str:
        """提交视频生成任务."""
        request_body = {
            "model": self._model,
            "input": {
                "prompt": prompt,
                "img_url": image_data,
            },
            "parameters": {
                "resolution": resolution,
                "duration": duration,
                "prompt_extend": True,
                "audio": enable_audio,
            },
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",  # 异步模式
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.SUBMIT_ENDPOINT,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

        # 检查错误
        if "code" in result and result["code"] != "":
            raise RuntimeError(f"Task submit failed: {result.get('code')} - {result.get('message')}")

        task_id = result.get("output", {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"No task_id in response: {result}")

        return task_id

    async def _wait_for_task(
        self,
        task_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 10,
    ) -> str:
        """等待任务完成并返回视频 URL."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        task_url = f"{self.TASK_ENDPOINT}/{task_id}"
        start_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 5

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(f"Task {task_id} timed out after {max_wait_seconds}s")

            try:
                # 查询任务状态（每次创建新客户端避免连接复用问题）
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(task_url, headers=headers)
                    response.raise_for_status()
                    result = response.json()

                # 重置连续错误计数
                consecutive_errors = 0

                output = result.get("output", {})
                status = output.get("task_status")

                if status == "SUCCEEDED":
                    video_url = output.get("video_url")
                    if not video_url:
                        raise RuntimeError(f"No video_url in completed task: {result}")
                    return video_url

                elif status == "FAILED":
                    error_code = output.get("code", "Unknown")
                    error_msg = output.get("message", "Unknown error")
                    raise RuntimeError(f"Task failed: {error_code} - {error_msg}")

                elif status in ("PENDING", "RUNNING"):
                    print(f"[Wanx] 任务状态: {status}, 已等待 {int(elapsed)}s...")
                    await asyncio.sleep(poll_interval)

                else:
                    raise RuntimeError(f"Unknown task status: {status}")

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                consecutive_errors += 1
                print(f"[Wanx] 轮询失败 ({consecutive_errors}/{max_consecutive_errors}): {type(e).__name__}")

                if consecutive_errors >= max_consecutive_errors:
                    raise RuntimeError(f"Too many consecutive polling errors: {e}")

                # 等待后重试
                await asyncio.sleep(poll_interval)

    async def _save_to_local_storage(self, remote_url: str, prompt: str, max_retries: int = 3) -> str:
        """下载视频并保存到本地存储（带重试）."""
        video_data = None
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.get(remote_url)
                    response.raise_for_status()
                    video_data = response.content
                    print(f"[Wanx] 视频下载成功 ({len(video_data)/1024/1024:.1f} MB)")
                    break
            except Exception as e:
                last_error = e
                print(f"[Wanx] 视频下载失败 (尝试 {attempt+1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        if video_data is None:
            raise RuntimeError(f"Failed to download video after {max_retries} attempts: {last_error}")

        # 生成文件名
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
        timestamp = int(time.time())
        filename = f"wanx_{prompt_hash}_{timestamp}.mp4"

        # 上传到本地存储
        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=video_data,
            key=filename,
            content_type="video/mp4",
        )

        if not result.success:
            raise ValueError(f"Failed to save video: {result.error}")

        return result.url
