# src/moana/services/image/minimax.py
"""MiniMax image generation service implementation.

生成的图片会自动保存到本地存储（example.com），
避免微信小程序的合法域名限制问题。
"""
import hashlib
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.image.base import BaseImageService, ImageResult, ImageStyle
from moana.services.storage import get_storage_service


class MiniMaxImageService(BaseImageService):
    """MiniMax image-01 图像生成服务.

    使用 MiniMax image-01 模型生成图像，价格仅 0.025元/张。
    """

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.minimax_api_key
        self._api_base = settings.minimax_api_base
        self._model = settings.minimax_image_model

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
        """使用 MiniMax image-01 生成图像."""
        enhanced_prompt = self.enhance_prompt_for_children(prompt, style)

        # 计算宽高比
        aspect_ratio = self._get_aspect_ratio(width, height)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/image_generation",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "prompt": enhanced_prompt,
                    "aspect_ratio": aspect_ratio,
                    "n": 1,
                },
            )
            response.raise_for_status()
            result = response.json()

        # Check for API errors first
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            error_code = base_resp.get("status_code")
            error_msg = base_resp.get("status_msg", "Unknown error")
            if error_code == 1008:
                raise ValueError(f"MiniMax Image error: Insufficient balance - {error_msg}")
            raise ValueError(f"MiniMax Image error [{error_code}]: {error_msg}")

        # 解析响应
        data = result.get("data")
        if data is None:
            raise ValueError("MiniMax Image error: No data in response")

        image_urls = data.get("image_urls", [])

        if not image_urls:
            # 兼容不同的响应格式
            remote_image_url = data.get("image_url", "")
        else:
            remote_image_url = image_urls[0]

        if not remote_image_url:
            raise ValueError("MiniMax Image error: No image URL in response")

        # 下载图片并保存到本地存储
        # 这样返回的 URL 是我们自己域名的，微信小程序可以正常访问
        local_image_url = await self._save_to_local_storage(
            remote_url=remote_image_url,
            prompt=enhanced_prompt,
        )

        return ImageResult(
            url=local_image_url,
            prompt=prompt,
            revised_prompt=enhanced_prompt,
            model=self._model,
            width=width,
            height=height,
        )

    async def _save_to_local_storage(
        self,
        remote_url: str,
        prompt: str,
    ) -> str:
        """下载远程图片并保存到本地存储.

        Args:
            remote_url: MiniMax 返回的临时 OSS URL
            prompt: 原始提示词（用于生成唯一文件名）

        Returns:
            本地存储 URL (https://example.com/media/images/...)
        """
        # 下载图片文件
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(remote_url)
            response.raise_for_status()
            image_data = response.content

        # 确定图片格式（从 URL 或 Content-Type 判断）
        content_type = response.headers.get("content-type", "image/jpeg")
        ext = "jpg"
        if "png" in content_type or remote_url.endswith(".png"):
            ext = "png"
        elif "webp" in content_type or remote_url.endswith(".webp"):
            ext = "webp"

        # 生成唯一的文件名（基于提示词的哈希）
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
        filename = f"img_{prompt_hash}.{ext}"

        # 上传到本地存储
        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=image_data,
            key=filename,
            content_type=content_type,
        )

        if not result.success:
            raise ValueError(f"Failed to save image to local storage: {result.error}")

        return result.url

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """将宽高转换为 MiniMax 支持的宽高比."""
        ratio = width / height

        # MiniMax 支持的宽高比: 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9, 1:1
        ratios = {
            "21:9": 21 / 9,
            "16:9": 16 / 9,
            "4:3": 4 / 3,
            "3:2": 3 / 2,
            "1:1": 1.0,
            "2:3": 2 / 3,
            "3:4": 3 / 4,
            "9:16": 9 / 16,
        }

        # 找到最接近的宽高比
        closest = min(ratios.keys(), key=lambda k: abs(ratios[k] - ratio))
        return closest
