from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MusicStyle(str, Enum):
    """Music style presets for children's songs."""
    CHEERFUL = "cheerful"
    GENTLE = "gentle"
    PLAYFUL = "playful"
    LULLABY = "lullaby"
    EDUCATIONAL = "educational"


@dataclass
class MusicResult:
    """Result of music generation."""
    audio_url: str
    duration: float  # in seconds
    lyrics: str
    model: str
    style: str = ""
    format: str = "mp3"
    # Extra metadata (e.g., all_tracks from Suno, cover_url, task_id)
    extra: dict[str, Any] = field(default_factory=dict)


class BaseMusicService(ABC):
    """Abstract base class for music generation services."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def generate(
        self,
        lyrics: str,
        style_prompt: str,
        duration_seconds: int = 45,
        style: MusicStyle = MusicStyle.CHEERFUL,
    ) -> MusicResult:
        """Generate music from lyrics."""
        pass

    def build_style_prompt(self, base_prompt: str, style: MusicStyle) -> str:
        """Build complete style prompt for children's music."""
        style_modifiers = {
            MusicStyle.CHEERFUL: "upbeat, happy, energetic rhythm",
            MusicStyle.GENTLE: "soft, calm, soothing melody",
            MusicStyle.PLAYFUL: "fun, bouncy, catchy tune",
            MusicStyle.LULLABY: "slow, peaceful, sleep-inducing",
            MusicStyle.EDUCATIONAL: "clear vocals, easy to follow",
        }

        modifier = style_modifiers.get(style, style_modifiers[MusicStyle.CHEERFUL])
        return f"{base_prompt}, {modifier}, children's song, Chinese, cute child voice"
