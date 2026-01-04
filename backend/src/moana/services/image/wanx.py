# src/moana/services/image/wanx.py
"""阿里百炼 Wanx 图片生成服务 (通义万相 Text-to-Image).

支持模型:
- wan2.6-t2i: 最新版本，支持同步接口
- wan2.5-t2i-preview: 支持自由尺寸
- wan2.2-t2i-flash: 极速版，速度快50%
- wan2.2-t2i-plus: 专业版，稳定性更好

API 文档: https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference
"""
import asyncio
import hashlib
import time
from http import HTTPStatus
from typing import Literal

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.image.base import BaseImageService, ImageResult, ImageStyle
from moana.services.storage import get_storage_service


class WanxImageService(BaseImageService):
    """阿里百炼通义万相文生图服务.

    使用 wan2.6-t2i 模型，支持同步接口，生成高质量图片。
    """

    # 同步接口端点 (wan2.6-t2i 专用)
    SYNC_API_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

    # 异步接口端点 (其他模型)
    ASYNC_API_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    TASK_API_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/tasks"

    # 可用模型
    MODELS = {
        "wan2.6-t2i": {"sync": True, "description": "最新版本，支持同步接口"},
        "wan2.5-t2i-preview": {"sync": False, "description": "支持自由尺寸"},
        "wan2.2-t2i-flash": {"sync": False, "description": "极速版，速度快50%"},
        "wan2.2-t2i-plus": {"sync": False, "description": "专业版，稳定性更好"},
    }

    def __init__(self, model: str | None = None):
        settings = get_settings()
        self._api_key = settings.dashscope_api_key
        self._model = model or settings.wanx_image_model
        self._use_sync = self.MODELS.get(self._model, {}).get("sync", False)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.STORYBOOK,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: str | None = None,
    ) -> ImageResult:
        """生成图片.

        Args:
            prompt: 正向提示词
            style: 图片风格
            width: 宽度 (512-1440)
            height: 高度 (512-1440)
            negative_prompt: 反向提示词

        Returns:
            ImageResult 包含图片 URL
        """
        # 增强提示词
        enhanced_prompt = self.enhance_prompt_for_children(prompt, style)

        # 默认反向提示词
        default_negative = "text, watermark, logo, signature, blurry, low quality, scary, violence, blood"
        final_negative = f"{negative_prompt}, {default_negative}" if negative_prompt else default_negative

        if self._use_sync:
            return await self._generate_sync(enhanced_prompt, final_negative, width, height)
        else:
            return await self._generate_async(enhanced_prompt, final_negative, width, height)

    async def _generate_sync(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
    ) -> ImageResult:
        """使用同步接口生成图片 (wan2.6-t2i).

        wan2.6-t2i 使用 messages 格式的请求体，不同于旧版 API。
        参考: https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference
        """
        request_data = {
            "model": self._model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": negative_prompt,
                "size": f"{width}*{height}",
                "n": 1,
                "prompt_extend": True,  # 启用智能改写
                "watermark": False,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.SYNC_API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "X-DashScope-Async": "disable",  # 同步模式
                },
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()

        # 解析响应 - wan2.6-t2i 使用 choices 格式
        # 响应路径: output.choices[].message.content[].image
        output = result.get("output", {})
        choices = output.get("choices", [])

        if not choices:
            raise ValueError(f"Wanx image generation failed: No choices in response. {result}")

        message = choices[0].get("message", {})
        content = message.get("content", [])

        if not content:
            raise ValueError(f"Wanx image generation failed: No content in response. {result}")

        image_url = content[0].get("image", "")
        revised_prompt = None  # wan2.6-t2i 不返回 revised_prompt

        if not image_url:
            raise ValueError("Wanx image generation failed: No image URL in response")

        # 下载并保存到本地存储
        local_url = await self._save_to_local_storage(image_url, prompt)

        return ImageResult(
            url=local_url,
            prompt=prompt,
            revised_prompt=revised_prompt,
            model=self._model,
            width=width,
            height=height,
        )

    async def _generate_async(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
    ) -> ImageResult:
        """使用异步接口生成图片 (其他模型)."""
        request_data = {
            "model": self._model,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
            },
            "parameters": {
                "size": f"{width}*{height}",
                "n": 1,
                "prompt_extend": True,
            },
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            # 1. 创建任务
            response = await client.post(
                self.ASYNC_API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "X-DashScope-Async": "enable",
                },
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()

            task_id = result.get("output", {}).get("task_id")
            if not task_id:
                raise ValueError(f"Wanx: No task_id in response: {result}")

            # 2. 轮询任务状态
            image_url = await self._wait_for_task(client, task_id)

        # 下载并保存到本地存储
        local_url = await self._save_to_local_storage(image_url, prompt)

        return ImageResult(
            url=local_url,
            prompt=prompt,
            revised_prompt=None,
            model=self._model,
            width=width,
            height=height,
        )

    async def _wait_for_task(
        self,
        client: httpx.AsyncClient,
        task_id: str,
        max_wait: int = 180,
        poll_interval: int = 3,
    ) -> str:
        """等待异步任务完成.

        Args:
            client: HTTP 客户端
            task_id: 任务 ID
            max_wait: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）

        Returns:
            图片 URL
        """
        start_time = time.time()
        task_url = f"{self.TASK_API_ENDPOINT}/{task_id}"

        while time.time() - start_time < max_wait:
            response = await client.get(
                task_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            result = response.json()

            status = result.get("output", {}).get("task_status")

            if status == "SUCCEEDED":
                results = result.get("output", {}).get("results", [])
                if results:
                    return results[0].get("url", "")
                raise ValueError("Wanx: Task succeeded but no image URL")

            elif status == "FAILED":
                error = result.get("output", {}).get("message", "Unknown error")
                raise RuntimeError(f"Wanx image generation failed: {error}")

            elif status in ("PENDING", "RUNNING"):
                await asyncio.sleep(poll_interval)
            else:
                raise RuntimeError(f"Wanx: Unknown task status: {status}")

        raise TimeoutError(f"Wanx: Task {task_id} timed out after {max_wait}s")

    async def _save_to_local_storage(self, remote_url: str, prompt: str) -> str:
        """下载远程图片并保存到本地存储.

        Args:
            remote_url: 远程图片 URL（有效期仅 24 小时）
            prompt: 原始提示词（用于生成唯一文件名）

        Returns:
            本地存储 URL (https://example.com/media/image/...)
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(remote_url)
            response.raise_for_status()
            image_data = response.content

        # 生成唯一文件名
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
        timestamp = int(time.time())
        filename = f"wanx_{prompt_hash}_{timestamp}.png"

        # 上传到本地存储
        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=image_data,
            key=filename,
            content_type="image/png",
        )

        if not result.success:
            raise ValueError(f"Failed to save image: {result.error}")

        return result.url
