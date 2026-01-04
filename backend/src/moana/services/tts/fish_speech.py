import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice


class FishSpeechService(BaseTTSService):
    """Fish Speech TTS service implementation."""

    DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # Placeholder

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.fish_speech_api_key
        self._api_base = settings.fish_speech_api_base

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        """Synthesize speech using Fish Speech API."""
        voice = voice_id or self.DEFAULT_VOICE

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/tts",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "reference_id": voice,
                    "speed": speed,
                    "format": "mp3",
                },
            )
            response.raise_for_status()
            result = response.json()

        return TTSResult(
            audio_url=result.get("audio_url", ""),
            duration=result.get("duration", 0.0),
            voice_id=voice,
            model="fish-speech-v1.5",
        )

    async def list_voices(self, language: str = "zh") -> list[Voice]:
        """List available voices."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._api_base}/v1/voices",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params={"language": language},
            )
            response.raise_for_status()
            data = response.json()

        return [
            Voice(
                id=v["id"],
                name=v["name"],
                language=v.get("language", language),
                gender=v.get("gender"),
                preview_url=v.get("preview_url"),
            )
            for v in data.get("voices", [])
        ]

    async def clone_voice(
        self,
        audio_url: str,
        name: str,
    ) -> Voice:
        """Clone a voice from audio sample (15-30 seconds)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/voices/clone",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "audio_url": audio_url,
                    "name": name,
                },
            )
            response.raise_for_status()
            data = response.json()

        return Voice(
            id=data["id"],
            name=name,
            language="zh",
        )
