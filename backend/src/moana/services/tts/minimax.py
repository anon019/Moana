# src/moana/services/tts/minimax.py
"""MiniMax TTS 语音合成服务."""
import base64

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice


class MiniMaxTTSService(BaseTTSService):
    """MiniMax Speech-02 语音合成服务.

    使用 MiniMax T2A v2 API.
    支持多语种、多音色、情感控制。
    端点: https://api.minimax.chat/v1/t2a_v2
    """

    # 预设音色列表 (MiniMax 实际可用的声音)
    VOICES = {
        "female-shaonv": {"name": "少女音", "gender": "female", "style": "活泼可爱"},
        "presenter_female": {"name": "主持人女声", "gender": "female", "style": "专业清晰"},
        "audiobook_female_1": {"name": "有声书女声", "gender": "female", "style": "温柔亲切"},
        "male-qn-qingse": {"name": "青涩男声", "gender": "male", "style": "青春活力"},
    }

    # 默认使用少女音，适合儿童内容
    DEFAULT_VOICE = "female-shaonv"

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.minimax_api_key
        # 使用正确的 API 端点
        self._api_base = "https://api.minimax.chat"
        self._model = "speech-02-turbo"  # 正确的模型名

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
        """合成语音.

        Args:
            text: 要合成的文本
            voice_id: 音色 ID，默认使用 female-shaonv（适合儿童内容）
            speed: 语速，0.5-2.0

        Returns:
            TTSResult 包含音频 URL 和元数据
        """
        voice = voice_id or self.DEFAULT_VOICE

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/t2a_v2",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "text": text,
                    "voice_setting": {
                        "voice_id": voice,
                        "speed": speed,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

        # 检查 API 响应状态
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            raise ValueError(f"MiniMax TTS error: {base_resp.get('status_msg', 'Unknown error')}")

        # 解析响应 - 返回的是十六进制编码的音频数据
        data = result.get("data", {})
        audio_hex = data.get("audio", "")

        # 转换为 base64 data URL
        if audio_hex:
            audio_bytes = bytes.fromhex(audio_hex)
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            audio_url = f"data:audio/mp3;base64,{audio_b64}"
            # 估算时长（假设 128kbps MP3）
            duration = len(audio_bytes) / (128 * 1024 / 8)
        else:
            audio_url = ""
            duration = 0.0

        return TTSResult(
            audio_url=audio_url,
            duration=duration,
            voice_id=voice,
            model=self._model,
        )

    async def list_voices(self, language: str = "zh") -> list[Voice]:
        """列出可用音色."""
        return [
            Voice(
                id=voice_id,
                name=info["name"],
                language=language,
                gender=info["gender"],
            )
            for voice_id, info in self.VOICES.items()
        ]

    async def clone_voice(
        self,
        audio_url: str,
        name: str,
    ) -> Voice:
        """克隆音色.

        MiniMax 支持快速声音克隆，价格 9.9元/个。
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._api_base}/v1/voice_clone",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "audio_url": audio_url,
                    "voice_name": name,
                },
            )
            response.raise_for_status()
            result = response.json()

        voice_id = result.get("data", {}).get("voice_id", "")

        return Voice(
            id=voice_id,
            name=name,
            language="zh",
        )
