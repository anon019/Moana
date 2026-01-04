from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Voice:
    """Voice information."""
    id: str
    name: str
    language: str
    gender: str | None = None
    preview_url: str | None = None


@dataclass
class TTSResult:
    """Result of TTS synthesis."""
    audio_url: str
    duration: float  # in seconds
    voice_id: str
    model: str


class BaseTTSService(ABC):
    """Abstract base class for TTS services."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        """Synthesize speech from text."""
        pass

    @abstractmethod
    async def list_voices(self, language: str = "zh") -> list[Voice]:
        """List available voices."""
        pass

    @abstractmethod
    async def clone_voice(
        self,
        audio_url: str,
        name: str,
    ) -> Voice:
        """Clone a voice from audio sample."""
        pass
