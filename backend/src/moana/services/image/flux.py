import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.image.base import BaseImageService, ImageResult, ImageStyle


class FluxService(BaseImageService):
    """Flux image generation service implementation."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.flux_api_key
        self._api_base = settings.flux_api_base

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
        """Generate an image using Flux API."""
        enhanced_prompt = self.enhance_prompt_for_children(prompt, style)

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Submit generation request
            response = await client.post(
                f"{self._api_base}/v1/flux-pro-1.1",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": enhanced_prompt,
                    "width": width,
                    "height": height,
                    "prompt_upsampling": True,
                    "safety_tolerance": 6,  # Strictest for children's content
                },
            )
            response.raise_for_status()
            result = response.json()

            # Poll for result
            task_id = result.get("id")
            if task_id:
                image_url = await self._poll_result(client, task_id)
            else:
                image_url = result.get("sample", result.get("url", ""))

        return ImageResult(
            url=image_url,
            prompt=prompt,
            revised_prompt=enhanced_prompt,
            model="flux-pro-1.1",
            width=width,
            height=height,
        )

    async def _poll_result(self, client: httpx.AsyncClient, task_id: str) -> str:
        """Poll for generation result."""
        import asyncio

        for _ in range(60):  # Max 60 attempts
            response = await client.get(
                f"{self._api_base}/v1/get_result",
                params={"id": task_id},
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("status") == "Ready":
                return result.get("result", {}).get("sample", "")

            await asyncio.sleep(2)

        raise TimeoutError("Image generation timed out")
