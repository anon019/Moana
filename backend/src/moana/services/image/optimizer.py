"""Image optimization utilities."""
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """Image format conversion and optimization."""

    @staticmethod
    def png_to_webp(
        png_data: bytes,
        quality: int = 90,
    ) -> bytes:
        """Convert PNG to WebP format.

        Args:
            png_data: Input PNG image bytes
            quality: WebP quality (0-100, default 90)

        Returns:
            WebP image bytes
        """
        img = Image.open(io.BytesIO(png_data))

        # Convert RGBA to RGB if needed (WebP supports both)
        if img.mode == "RGBA":
            # Keep alpha channel for WebP
            pass
        elif img.mode != "RGB":
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format="WEBP", quality=quality, method=4)
        webp_data = output.getvalue()

        logger.info(
            f"Converted PNG ({len(png_data)} bytes) to WebP ({len(webp_data)} bytes), "
            f"ratio: {len(webp_data) / len(png_data):.1%}"
        )
        return webp_data

    @staticmethod
    def generate_thumbnail(
        image_data: bytes,
        size: int = 256,
        quality: int = 85,
    ) -> bytes:
        """Generate a thumbnail in WebP format.

        Args:
            image_data: Input image bytes (PNG or WebP)
            size: Thumbnail size (width and height, default 256)
            quality: WebP quality (0-100, default 85)

        Returns:
            Thumbnail WebP bytes
        """
        img = Image.open(io.BytesIO(image_data))

        # Use LANCZOS for high-quality downscaling
        img.thumbnail((size, size), Image.Resampling.LANCZOS)

        # Convert to RGB if needed
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format="WEBP", quality=quality, method=4)
        thumb_data = output.getvalue()

        logger.info(
            f"Generated {size}x{size} thumbnail ({len(thumb_data)} bytes)"
        )
        return thumb_data
