# src/moana/services/tts/qwen.py
"""阿里云 Qwen TTS 语音合成服务.

使用 WebSocket API (qwen3-tts-flash-realtime) 支持完整音色列表。
API 文档: https://help.aliyun.com/zh/model-studio/qwen-tts-realtime

生成的音频会自动保存到本地存储（example.com），
避免微信小程序的合法域名限制问题。
"""
import asyncio
import base64
import hashlib
import json
import uuid

import websockets
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.tts.base import BaseTTSService, TTSResult, Voice
from moana.services.storage import get_storage_service


class QwenTTSService(BaseTTSService):
    """Qwen3-TTS-Flash-Realtime 语音合成服务.

    使用 WebSocket API 支持 40+ 音色。
    """

    # 预设音色列表 - 仅包含实际测试验证可用的音色
    # 注意：阿里云文档列出的音色与实际 API 支持的不一致，以下为 2024-12 验证可用的音色
    VOICES = {
        # 女声
        "Cherry": {"name": "Cherry", "name_cn": "芊悦", "gender": "female", "style": "温柔亲切", "description": "适合儿童故事、睡前读物（推荐）"},
        "Jennifer": {"name": "Jennifer", "name_cn": "詹妮弗", "gender": "female", "style": "清晰标准", "description": "适合教育内容、科普讲解"},
        "Kiki": {"name": "Kiki", "name_cn": "阿清", "gender": "female", "style": "粤语女声", "description": "适合粤语内容"},
        # 男声
        "Ethan": {"name": "Ethan", "name_cn": "晨煦", "gender": "male", "style": "成熟稳重", "description": "适合叙述性内容、故事旁白"},
        "Ryan": {"name": "Ryan", "name_cn": "甜茶", "gender": "male", "style": "温暖亲和", "description": "适合父亲角色、教育引导"},
        "Nofish": {"name": "Nofish", "name_cn": "不吃鱼", "gender": "male", "style": "活泼有趣", "description": "适合趣味内容、动画配音"},
    }

    # 默认音色（适合儿童内容）
    DEFAULT_VOICE = "Cherry"

    @classmethod
    def get_voice_options(cls) -> list[dict]:
        """获取所有可用音色选项（供 API 返回给前端）."""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "name_cn": info["name_cn"],
                "gender": info["gender"],
                "style": info["style"],
                "description": info["description"],
                "recommended": voice_id == "Cherry",  # 推荐用于儿童内容
            }
            for voice_id, info in cls.VOICES.items()
        ]

    # WebSocket API 端点
    WS_ENDPOINT = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-flash-realtime"

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.dashscope_api_key
        self._model = "qwen3-tts-flash-realtime"

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
            voice_id: 音色 ID，默认使用 Cherry（适合儿童内容）
            speed: 语速，0.5-2.0

        Returns:
            TTSResult 包含音频 URL 和元数据
            音频会自动保存到本地存储，返回本地 URL
        """
        # 验证音色是否支持，不支持则 fallback 到默认音色
        voice = voice_id or self.DEFAULT_VOICE
        if voice not in self.VOICES:
            print(f"[TTS Warning] Voice '{voice}' not supported, falling back to '{self.DEFAULT_VOICE}'")
            voice = self.DEFAULT_VOICE

        task_id = str(uuid.uuid4())

        # 收集音频数据
        audio_chunks = []

        try:
            async with websockets.connect(
                self.WS_ENDPOINT,
                additional_headers={"Authorization": f"Bearer {self._api_key}"},
                ping_interval=20,
                ping_timeout=60,
                close_timeout=10,
            ) as ws:
                # 1. 等待 session.created
                response = await asyncio.wait_for(ws.recv(), timeout=10)
                msg = json.loads(response)
                if msg.get("type") != "session.created":
                    raise ValueError(f"Expected session.created, got: {msg}")

                # 2. 发送 session.update 配置
                session_update = {
                    "type": "session.update",
                    "session": {
                        "mode": "server_commit",
                        "voice": voice,
                        "language_type": "Auto",
                        "response_format": "mp3",
                        "sample_rate": 24000,
                    }
                }
                await ws.send(json.dumps(session_update))

                # 3. 等待 session.updated 确认
                response = await asyncio.wait_for(ws.recv(), timeout=10)
                msg = json.loads(response)
                if msg.get("type") == "error":
                    raise ValueError(f"Session update failed: {msg.get('error', {}).get('message', 'Unknown error')}")

                # 4. 发送文本
                text_event = {
                    "type": "input_text_buffer.append",
                    "text": text,
                }
                await ws.send(json.dumps(text_event))

                # 5. 发送提交信号
                commit_event = {
                    "type": "input_text_buffer.commit",
                }
                await ws.send(json.dumps(commit_event))

                # 6. 接收音频数据
                while True:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=60)
                        msg = json.loads(response)
                        msg_type = msg.get("type")

                        if msg_type == "response.audio.delta":
                            # 音频数据块
                            audio_base64 = msg.get("delta", "")
                            if audio_base64:
                                audio_chunks.append(base64.b64decode(audio_base64))

                        elif msg_type == "response.audio.done":
                            # 音频生成完成
                            pass

                        elif msg_type == "response.done":
                            # 响应完成，发送 session.finish
                            finish_event = {"type": "session.finish"}
                            await ws.send(json.dumps(finish_event))

                        elif msg_type == "session.finished":
                            # 会话结束
                            break

                        elif msg_type == "error":
                            error_msg = msg.get("error", {}).get("message", "Unknown error")
                            raise ValueError(f"TTS error: {error_msg}")

                    except asyncio.TimeoutError:
                        print(f"[TTS Warning] Timeout waiting for response, collected {len(audio_chunks)} chunks")
                        break

        except websockets.exceptions.WebSocketException as e:
            print(f"[TTS Error] WebSocket error: {e}")
            raise ValueError(f"WebSocket connection failed: {e}")

        if not audio_chunks:
            raise ValueError("No audio data received")

        # 合并音频数据
        audio_data = b"".join(audio_chunks)

        # 保存到本地存储
        local_audio_url = await self._save_to_local_storage(
            audio_data=audio_data,
            text=text,
        )

        # 估算时长（基于文本长度，约每秒5个字）
        estimated_duration = len(text) / 5.0

        return TTSResult(
            audio_url=local_audio_url,
            duration=estimated_duration,
            voice_id=voice,
            model=self._model,
        )

    async def _save_to_local_storage(
        self,
        audio_data: bytes,
        text: str,
    ) -> str:
        """保存音频到本地存储.

        Args:
            audio_data: 音频二进制数据
            text: 原始文本（用于生成唯一文件名）

        Returns:
            本地存储 URL (https://example.com/media/audio/...)
        """
        # 生成唯一的文件名（基于文本内容的哈希）
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        filename = f"tts_{text_hash}.mp3"

        # 上传到本地存储
        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=audio_data,
            key=filename,
            content_type="audio/mpeg",
        )

        if not result.success:
            raise ValueError(f"Failed to save audio to local storage: {result.error}")

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

    async def clone_voice(
        self,
        audio_url: str,
        name: str,
    ) -> Voice:
        """克隆音色（需要额外配置）.

        注意：声音复刻需要使用专门的 API 端点。
        """
        raise NotImplementedError(
            "Voice cloning requires Qwen-TTS-Realtime voice replica API. "
            "See: https://help.aliyun.com/zh/model-studio/qwen-tts-realtime-voice-replica"
        )
