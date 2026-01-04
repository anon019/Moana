# src/moana/pipelines/video.py
"""视频生成 Pipeline - 将绘本转换为动态视频."""
import logging
from dataclasses import dataclass
from typing import Any, Callable

from moana.services.video import get_video_service
from moana.services.video.base import BaseVideoService, VideoResult

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Progress tracking for video generation."""
    stage: str
    current: int
    total: int
    message: str


class VideoPipeline:
    """Pipeline for generating video from picture book.

    将绘本转换为动态视频。

    流程（优化后）：
    1. 提取第一张和最后一张插图
    2. 合并所有页面文本作为 prompt
    3. 一次 API 调用生成完整视频（节省配额）
    """

    def __init__(
        self,
        video_service: BaseVideoService | None = None,
    ):
        self._video_service = video_service or get_video_service()

    async def generate(
        self,
        picture_book_data: dict[str, Any],
        on_progress: Callable[[GenerationProgress], None] | None = None,
    ) -> dict[str, Any]:
        """从绘本数据生成视频.

        优化：一个绘本只调用一次 Veo API，使用第一张和最后一张图片。
        Veo 3.1 配额：每分钟 2 次，每天 10 次。

        Args:
            picture_book_data: 绘本数据，包含 title 和 pages
            on_progress: 进度回调函数

        Returns:
            包含视频 URL 和元数据的字典
        """
        title = picture_book_data.get("title", "未命名视频")
        pages = picture_book_data.get("pages", [])

        if not pages:
            raise ValueError("绘本数据中没有页面")

        # 提取第一张和最后一张图片
        first_page = pages[0]
        last_page = pages[-1] if len(pages) > 1 else None

        first_image_url = first_page.get("image_url", "")
        last_image_url = last_page.get("image_url", "") if last_page else None

        if not first_image_url:
            raise ValueError("绘本第一页没有图片")

        # 合并所有页面文本作为 prompt
        all_texts = [page.get("text", "") for page in pages if page.get("text")]
        combined_prompt = f"儿童绘本故事动画：{title}。" + " ".join(all_texts)
        # 限制 prompt 长度
        if len(combined_prompt) > 500:
            combined_prompt = combined_prompt[:500] + "..."

        logger.info(f"Generating single video for picture book: {title}")
        logger.info(f"Using first image: {first_image_url[:50]}...")
        if last_image_url:
            logger.info(f"Using last image: {last_image_url[:50]}...")

        # Stage 1: 生成视频（单次 API 调用）
        if on_progress:
            on_progress(GenerationProgress(
                stage="video_generation",
                current=0,
                total=1,
                message="正在生成视频...",
            ))

        video_result = await self._video_service.generate(
            image_url=first_image_url,
            prompt=combined_prompt,
            duration_seconds=8,  # Veo 最大支持 8 秒
            last_frame_url=last_image_url,
        )

        if on_progress:
            on_progress(GenerationProgress(
                stage="video_generation",
                current=1,
                total=1,
                message="视频生成完成",
            ))

        return {
            "title": title,
            "video_url": video_result.video_url,
            "duration": video_result.duration,
            "thumbnail_url": first_image_url,
            "clips": [
                {
                    "page_num": 1,
                    "video_url": video_result.video_url,
                    "duration": video_result.duration,
                }
            ],
            "generated_by": {
                "video_model": video_result.model,
            },
        }

    # 注：旧的多片段拼接方法已移除，现在一个绘本只生成一个视频
