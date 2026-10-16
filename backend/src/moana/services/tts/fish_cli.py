"""通过受控 CLI 生成免费语音，无 Google 或付费后端回退。"""

import asyncio
from contextlib import asynccontextmanager
import fcntl
import io
import json
import math
import os
from pathlib import Path
import re
import signal
import tempfile
import uuid
import wave

from moana.config import get_settings
from moana.services.audio.converter import AudioConverter
from moana.services.storage import get_storage_service
from moana.services.tts.base import BaseTTSService, TTSResult, Voice
from moana.services.tts.cli_worker import FISH_FREE_MODEL, fish_free_available

MEDIA_CLI_LOCK = "/tmp/kids-media-cli.lock"
LEGACY_VOICES = {"Kore", "Leda", "Aoede", "Puck", "Charon", "Fenrir", "Cherry", "fish-default"}


@asynccontextmanager
async def media_cli_lock():
    """与图片 CLI 共享全机锁；取消排队时立即释放文件句柄。"""
    with open(MEDIA_CLI_LOCK, "a") as handle:
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                await asyncio.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


class FishFreeCLIService(BaseTTSService):
    DEFAULT_VOICE = "fish-default"
    MODEL = FISH_FREE_MODEL
    ENGINE = "fish_free"

    def __init__(self):
        settings = get_settings()
        self._python = settings.tts_cli_python
        self._timeout = settings.tts_cli_timeout
        self._fish_key = settings.fish_speech_api_key
        self._voice_id = settings.fish_speech_voice_id.strip()
        if not 0 < self._timeout <= 240:
            raise ValueError("TTS CLI 超时须介于 0 和 240 秒。")

    @property
    def model_name(self) -> str:
        return self.MODEL

    def validate_configuration(self, voice_id: str | None = None) -> str:
        """出图前预检免费服务配置；构造与列音色无需凭证。"""
        if not Path(self._python).is_file():
            raise ValueError("找不到 TTS CLI Python；请检查 TTS_CLI_PYTHON。")
        if not fish_free_available():
            raise ValueError("Fish 免费期限已结束；已拒绝请求，不会转付费模型。")
        if not self._fish_key.strip():
            raise ValueError("Fish 免费托管服务未配置 FISH_SPEECH_API_KEY；请在服务器安全配置中添加。")
        if voice_id is not None and not isinstance(voice_id, str):
            raise ValueError("Fish 声音 ID 必须为字符串")
        voice = voice_id or self._voice_id
        if voice in LEGACY_VOICES:
            voice = self._voice_id
        if not isinstance(voice, str) or not re.fullmatch(r"[a-fA-F0-9]{32}", voice):
            raise ValueError("请配置 FISH_SPEECH_VOICE_ID 为 Fish 语音库中的 32 位声音 ID。")
        return voice

    async def _generate(self, text: str, speed: float, voice_id: str | None) -> bytes:
        voice_id = self.validate_configuration(voice_id)
        env = {key: value for key, value in os.environ.items() if key in {
            "HOME", "PATH", "LANG", "LC_ALL", "TZ", "SSL_CERT_FILE", "SSL_CERT_DIR",
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
            "http_proxy", "https_proxy", "all_proxy", "no_proxy",
        }}
        env["FISH_SPEECH_API_KEY"] = self._fish_key
        with tempfile.TemporaryDirectory(prefix="kids-tts-") as directory:
            output = Path(directory) / "audio.wav"
            command = [self._python, str(Path(__file__).with_name("cli_worker.py")),
                       "--output", str(output)]
            process = await asyncio.create_subprocess_exec(
                *command, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL, env=env, start_new_session=True,
            )
            try:
                await process.communicate(json.dumps({
                    "text": text, "speed": speed,
                    "voice_id": voice_id,
                }, ensure_ascii=False).encode())
            finally:
                if process.returncode is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    await process.wait()
            if process.returncode != 0 or not output.is_file():
                raise RuntimeError("Fish 免费 TTS CLI 合成失败；请检查网络、Key 和声音 ID。")
            if not 44 < output.stat().st_size <= 12 * 1024 * 1024:
                raise RuntimeError("TTS CLI 音频为空或超出大小限制。")
            return output.read_bytes()

    async def synthesize(self, text: str, voice_id: str | None = None,
                         speed: float = 1.0) -> TTSResult:
        if not isinstance(text, str) or not text.strip() or len(text) > 1000:
            raise ValueError("语音文本须为 1 至 1000 字符。")
        if (isinstance(speed, bool) or not isinstance(speed, (int, float))
                or not 0.5 <= speed <= 2 or not math.isfinite(speed)):
            raise ValueError("语速须介于 0.5 和 2.0。")
        voice = self.validate_configuration(voice_id)
        # 单次总预算包含排队、子进程、格式转换与存储，不叠加重试。
        async with asyncio.timeout(self._timeout):
            async with media_cli_lock():
                wav_data = await self._generate(text, speed, voice)
                with wave.open(io.BytesIO(wav_data), "rb") as audio:
                    # 流式 WAV 的长度头可能未回填，以实际样本数计算时长。
                    samples = audio.readframes(audio.getnframes())
                    duration = len(samples) / (audio.getsampwidth() * audio.getnchannels() * audio.getframerate())
                    if duration <= 0:
                        raise RuntimeError("Fish 没有返回有效的音频样本。")
                mp3 = await AudioConverter.wav_to_mp3(wav_data)
                result = await get_storage_service().upload_bytes(
                    mp3, f"audio/{self.ENGINE}/{uuid.uuid4().hex}.mp3", "audio/mpeg",
                )
                if not result.success or not result.url:
                    raise RuntimeError("语音生成成功但保存失败；请检查媒体存储。")
        return TTSResult(result.url, duration, voice, self.MODEL)

    async def list_voices(self, language: str = "zh") -> list[Voice]:
        if language not in {"zh", "zh-CN", "zh_CN"}:
            return []
        return [Voice(self._voice_id, "Fish 中文旁白", "zh")] if self._voice_id else []

    async def close(self):
        """无常驻进程或连接；每次调用退出时均已回收。"""

    async def clone_voice(self, audio_url: str, name: str) -> Voice:
        raise NotImplementedError("免费语音 CLI 不提供声音克隆。")
