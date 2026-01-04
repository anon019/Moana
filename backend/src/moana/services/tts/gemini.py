"""Google Gemini TTS 语音合成服务.

使用 Gemini 2.5 Flash TTS 模型生成语音。
文档: https://ai.google.dev/gemini-api/docs/speech-generation
"""
import asyncio
import hashlib
import io
import logging
import struct
import wave

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice
from moana.services.storage import get_storage_service
from moana.services.audio import AudioConverter

logger = logging.getLogger(__name__)


class GeminiTTSService(BaseTTSService):
    """Gemini 2.5 Flash TTS 语音合成服务实现."""

    # Gemini 预设音色
    # 参考: https://ai.google.dev/gemini-api/docs/speech-generation
    VOICES = {
        "Kore": {
            "name": "Kore",
            "name_cn": "温暖女声",
            "gender": "female",
            "style": "温暖亲切",
            "description": "适合儿童故事（推荐）",
        },
        "Puck": {
            "name": "Puck",
            "name_cn": "活泼中性",
            "gender": "neutral",
            "style": "活泼有趣",
            "description": "适合趣味内容",
        },
        "Charon": {
            "name": "Charon",
            "name_cn": "沉稳男声",
            "gender": "male",
            "style": "沉稳大气",
            "description": "适合旁白叙述",
        },
        "Aoede": {
            "name": "Aoede",
            "name_cn": "清晰女声",
            "gender": "female",
            "style": "清晰标准",
            "description": "适合教育内容",
        },
        "Fenrir": {
            "name": "Fenrir",
            "name_cn": "深沉男声",
            "gender": "male",
            "style": "深沉有力",
            "description": "适合故事角色",
        },
        "Leda": {
            "name": "Leda",
            "name_cn": "柔和女声",
            "gender": "female",
            "style": "柔和舒缓",
            "description": "适合睡前故事",
        },
    }

    DEFAULT_VOICE = "Kore"

    @classmethod
    def get_voice_options(cls) -> list[dict]:
        """获取所有可用音色选项."""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "name_cn": info["name_cn"],
                "gender": info["gender"],
                "style": info["style"],
                "description": info["description"],
                "recommended": voice_id == "Kore",
            }
            for voice_id, info in cls.VOICES.items()
        ]

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.google_api_key
        self._model = settings.gemini_tts_model
        self._default_voice = settings.gemini_tts_voice
        self._client = genai.Client(api_key=self._api_key)
        logger.info(f"GeminiTTSService initialized with model: {self._model}")

    @property
    def model_name(self) -> str:
        """返回当前使用的模型名称."""
        return self._model

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
            voice_id: 音色 ID，默认使用 Kore
            speed: 语速（Gemini TTS 暂不支持，保留参数兼容性）

        Returns:
            TTSResult 包含音频 URL 和元数据
        """
        voice = voice_id or self._default_voice
        if voice not in self.VOICES:
            logger.warning(
                f"Voice '{voice}' not supported, falling back to '{self.DEFAULT_VOICE}'"
            )
            voice = self.DEFAULT_VOICE

        logger.info(f"Synthesizing with Gemini TTS, voice={voice}: {text[:50]}...")

        # Gemini TTS 使用 generate_content API
        # 使用明确的 TTS 指令格式，避免模型尝试生成文本回复
        tts_prompt = f"Read aloud the following text exactly as written, do not add any commentary: {text}"

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.models.generate_content(
                model=self._model,
                contents=tts_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            ),
        )

        # 从响应中提取音频
        audio_data = None
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    mime_type = getattr(part.inline_data, "mime_type", "")
                    if mime_type.startswith("audio/"):
                        audio_data = part.inline_data.data
                        break

        if not audio_data:
            raise RuntimeError("No audio generated by Gemini TTS")

        logger.info(f"Generated {len(audio_data)} bytes audio")

        # 保存到本地存储
        local_url = await self._save_to_storage(audio_data, text)

        # 估算时长（基于文本长度，中文约每秒 4-5 个字）
        estimated_duration = len(text) / 4.5

        return TTSResult(
            audio_url=local_url,
            duration=estimated_duration,
            voice_id=voice,
            model=self._model,
        )

    def _pcm_to_wav(
        self,
        pcm_data: bytes,
        sample_rate: int = 24000,
        channels: int = 1,
        sample_width: int = 2,  # 16-bit = 2 bytes
    ) -> bytes:
        """将 PCM 数据转换为 WAV 格式.

        Gemini TTS 返回 audio/L16;codec=pcm;rate=24000 格式的原始 PCM 数据，
        需要添加 WAV 头才能被浏览器正确播放。

        Args:
            pcm_data: 原始 PCM 音频数据
            sample_rate: 采样率，默认 24000 Hz
            channels: 声道数，默认 1（单声道）
            sample_width: 采样位宽，默认 2（16-bit）

        Returns:
            WAV 格式的音频数据
        """
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        return wav_buffer.getvalue()

    async def _save_to_storage(self, audio_data: bytes, text: str) -> str:
        """保存音频到存储.

        将 PCM 转换为 WAV，再转换为 AAC 格式以减小文件大小。
        AAC 96kbps 对语音内容质量足够，文件比 WAV 小约 75%。
        """
        # 将 PCM 转换为 WAV 格式
        wav_data = self._pcm_to_wav(audio_data)
        logger.info(f"Converted PCM ({len(audio_data)} bytes) to WAV ({len(wav_data)} bytes)")

        # 将 WAV 转换为 AAC 格式
        try:
            aac_data = await AudioConverter.wav_to_aac(wav_data, bitrate="96k")
            audio_bytes = aac_data
            file_ext = "m4a"
            content_type = "audio/mp4"
            logger.info(f"Converted to AAC ({len(aac_data)} bytes)")
        except Exception as e:
            # Fallback to WAV if AAC conversion fails
            logger.warning(f"AAC conversion failed, using WAV: {e}")
            audio_bytes = wav_data
            file_ext = "wav"
            content_type = "audio/wav"

        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        filename = f"tts_{text_hash}.{file_ext}"

        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=audio_bytes,
            key=filename,
            content_type=content_type,
        )

        if not result.success:
            raise RuntimeError(f"Failed to save audio: {result.error}")

        logger.info(f"Audio saved to: {result.url}")
        return result.url

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

    async def clone_voice(self, audio_url: str, name: str) -> Voice:
        """克隆音色（Gemini TTS 不支持）."""
        raise NotImplementedError("Gemini TTS does not support voice cloning")
