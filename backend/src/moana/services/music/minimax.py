import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.music.base import BaseMusicService, MusicResult, MusicStyle


class MiniMaxMusicService(BaseMusicService):
    """MiniMax Music 2.0 service implementation."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.minimax_api_key
        self._api_base = settings.minimax_api_base
        self._model = settings.minimax_music_model

    @property
    def provider_name(self) -> str:
        return "minimax"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        lyrics: str,
        style_prompt: str,
        duration_seconds: int = 45,
        style: MusicStyle = MusicStyle.CHEERFUL,
    ) -> MusicResult:
        """Generate music using MiniMax Music 2.0 API."""
        full_style_prompt = self.build_style_prompt(style_prompt, style)

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/music_generation",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "prompt": full_style_prompt,
                    "lyrics": lyrics,
                    "output_format": "url",  # Get URL directly instead of hex
                    "audio_setting": {
                        "sample_rate": 44100,
                        "bitrate": 128000,
                        "format": "mp3",
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

        # Parse MiniMax response format
        # Response structure: {data: {audio: "url"}, extra_info: {music_duration: ms}}
        data = result.get("data", {})
        extra_info = result.get("extra_info", {})

        audio_url = data.get("audio", "")
        duration_ms = extra_info.get("music_duration", 0)
        duration_seconds = duration_ms / 1000.0  # Convert ms to seconds

        return MusicResult(
            audio_url=audio_url,
            duration=duration_seconds,
            lyrics=lyrics,
            model=self._model,
            style=style.value,
            format="mp3",
        )
