"""独立 Fish 免费托管语音 CLI，不加载本地模型。"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import resource
import sys
import urllib.request
import wave

FISH_FREE_MODEL = "s2.1-pro-free"
FISH_FREE_DEADLINE = datetime(2026, 12, 1, tzinfo=timezone.utc)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """拒绝跳转，确保授权和固定免费模型头只发送到指定服务。"""

    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


def fish_free_available(now=None):
    return (now or datetime.now(timezone.utc)) < FISH_FREE_DEADLINE


def generate_fish(text: str, speed: float, output: Path, voice_id: str | None):
    if not fish_free_available():
        raise ValueError("Fish 免费期限已结束；拒绝请求，也不会切换付费模型。")
    key = os.environ.get("FISH_SPEECH_API_KEY", "").strip()
    if not key:
        raise ValueError("Fish 免费托管服务需要配置 FISH_SPEECH_API_KEY。")
    if not isinstance(voice_id, str) or not re.fullmatch(r"[a-fA-F0-9]{32}", voice_id):
        raise ValueError("Fish CLI 需要有效的 32 位 reference_id。")
    body = {"text": text, "format": "wav", "sample_rate": 24000,
            "prosody": {"speed": speed}, "reference_id": voice_id}
    request = urllib.request.Request(
        "https://api.fish.audio/v1/tts", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "model": FISH_FREE_MODEL}, method="POST",
    )
    # 不重试，不解析错误响应/打印正文，避免泄漏文本或凭据。
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=60) as response, output.open("wb") as stream:
        total = 0
        while chunk := response.read(16384):
            total += len(chunk)
            if total > 12 * 1024 * 1024:
                raise ValueError("Fish 音频超过单次大小限制。")
            stream.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="Kids 免费语音 CLI")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # 子进程独立限制，不修改服务主进程的资源设置。
    resource.setrlimit(resource.RLIMIT_AS, (384 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024,) * 2)
    os.nice(10)
    data = json.loads(sys.stdin.buffer.read(8193))
    text = data.get("text")
    speed = data.get("speed", 1.0)
    if not isinstance(text, str) or not text.strip() or len(text) > 1000:
        raise ValueError("语音文本须为 1 至 1000 字符。")
    if isinstance(speed, bool) or not isinstance(speed, (int, float)) or not 0.5 <= speed <= 2:
        raise ValueError("语速须介于 0.5 和 2.0。")
    temporary = args.output.with_suffix(args.output.suffix + ".part")
    try:
        generate_fish(text, speed, temporary, data.get("voice_id"))
        with wave.open(str(temporary), "rb") as audio:
            if audio.getnframes() <= 0 or audio.getframerate() <= 0:
                raise ValueError("语音 CLI 没有生成有效音频。")
        temporary.replace(args.output)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("语音 CLI 失败；请检查网络、资源或 Fish 免费服务配置。", file=sys.stderr)
        sys.exit(1)
