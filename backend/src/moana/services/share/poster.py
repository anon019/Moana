# src/moana/services/share/poster.py
from dataclasses import dataclass
from typing import Optional
from io import BytesIO


@dataclass
class PosterConfig:
    """Configuration for poster generation."""
    width: int = 750
    height: int = 1334
    title_font_size: int = 48
    subtitle_font_size: int = 32
    qr_size: int = 200
    background_color: str = "#FFFFFF"
    title_color: str = "#333333"
    subtitle_color: str = "#666666"


@dataclass
class PosterResult:
    """Result of poster generation."""
    success: bool
    image_bytes: Optional[bytes] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "has_image": self.image_bytes is not None,
            "error": self.error,
        }


class PosterService:
    """Service for generating share posters."""

    def __init__(self, config: Optional[PosterConfig] = None):
        self.config = config or PosterConfig()

    async def generate_poster(
        self,
        title: str,
        subtitle: str,
        cover_image_url: Optional[str] = None,
        qr_data: Optional[str] = None,
        child_name: Optional[str] = None,
    ) -> PosterResult:
        """Generate a share poster.

        Args:
            title: Content title
            subtitle: Content subtitle/description
            cover_image_url: URL of cover image
            qr_data: Data for QR code
            child_name: Name of the child

        Returns:
            PosterResult with image bytes
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import qrcode
        except ImportError:
            return PosterResult(
                success=False,
                error="Pillow or qrcode not installed",
            )

        try:
            # Create base image
            img = Image.new(
                "RGB",
                (self.config.width, self.config.height),
                self.config.background_color,
            )
            draw = ImageDraw.Draw(img)

            # Try to load fonts (fallback to default if not available)
            try:
                title_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    self.config.title_font_size,
                )
                subtitle_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    self.config.subtitle_font_size,
                )
            except (OSError, IOError):
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

            # Draw title
            y_position = 100
            draw.text(
                (self.config.width // 2, y_position),
                title,
                fill=self.config.title_color,
                font=title_font,
                anchor="mt",
            )

            # Draw subtitle
            y_position += 80
            draw.text(
                (self.config.width // 2, y_position),
                subtitle,
                fill=self.config.subtitle_color,
                font=subtitle_font,
                anchor="mt",
            )

            # Draw child name if provided
            if child_name:
                y_position += 60
                draw.text(
                    (self.config.width // 2, y_position),
                    f"— {child_name} 的专属内容 —",
                    fill=self.config.subtitle_color,
                    font=subtitle_font,
                    anchor="mt",
                )

            # Generate and place QR code if data provided
            if qr_data:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=2,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img = qr_img.resize((self.config.qr_size, self.config.qr_size))

                # Place QR code at bottom center
                qr_x = (self.config.width - self.config.qr_size) // 2
                qr_y = self.config.height - self.config.qr_size - 100
                img.paste(qr_img, (qr_x, qr_y))

                # Add QR code label
                draw.text(
                    (self.config.width // 2, qr_y + self.config.qr_size + 20),
                    "扫码查看",
                    fill=self.config.subtitle_color,
                    font=subtitle_font,
                    anchor="mt",
                )

            # Convert to bytes
            output = BytesIO()
            img.save(output, format="PNG")
            image_bytes = output.getvalue()

            return PosterResult(
                success=True,
                image_bytes=image_bytes,
            )

        except Exception as e:
            return PosterResult(
                success=False,
                error=str(e),
            )

    async def generate_simple_poster(
        self,
        text: str,
        qr_data: Optional[str] = None,
    ) -> PosterResult:
        """Generate a simple text-based poster.

        Args:
            text: Main text content
            qr_data: Data for QR code

        Returns:
            PosterResult with image bytes
        """
        return await self.generate_poster(
            title=text,
            subtitle="",
            qr_data=qr_data,
        )
