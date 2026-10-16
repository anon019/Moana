#!/usr/bin/env python3
"""为当前 Fish Audio 在线语音 CLI 生成中文音色预览；串行执行，失败即停。"""
# ruff: noqa: E402
import argparse
import asyncio
from pathlib import Path
import re
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from moana.config import get_settings
from moana.services.storage import get_storage_service
from moana.services.tts import get_tts_service

PREVIEW_TEXT = "小朋友你好呀，让我来给你讲一个有趣的故事吧！我们一起观察，慢慢发现。"


async def generate_and_save_previews(force: bool = False) -> dict[str, str]:
    settings = get_settings()
    provider = settings.tts_provider.strip().lower()
    if provider not in {"fish_speech", "fish_audio", "fish_free_cli"}:
        raise ValueError("预览脚本只允许 Fish Audio 在线语音 CLI；请先设置 TTS_PROVIDER=fish_speech")
    provider = "fish_speech"
    service, storage = get_tts_service(), get_storage_service()
    results = {}
    try:
        for voice in await service.list_voices(language="zh"):
            if not re.fullmatch(r"[A-Za-z0-9_-]+", voice.id):
                raise ValueError("音色标识包含非法路径字符")
            key = f"voice-preview/{provider}/{voice.id}.mp3"
            cached = Path(settings.storage_local_path) / key
            if not force and cached.is_file():
                results[voice.id] = settings.storage_base_url.rstrip("/") + "/" + key
                continue
            service.validate_configuration(voice.id)
            result = await service.synthesize(PREVIEW_TEXT, voice_id=voice.id)
            base = settings.storage_base_url.rstrip("/") + "/"
            if not result.audio_url.startswith(base):
                raise ValueError("语音服务返回了无法受控导入的媒体地址")
            media_root = Path(settings.storage_local_path).resolve()
            source = (media_root / result.audio_url[len(base):]).resolve()
            if not source.is_relative_to(media_root) or not source.is_file():
                raise ValueError("语音 CLI 返回了无效媒体路径")
            upload = await storage.upload_bytes(data=source.read_bytes(), key=key, content_type="audio/mpeg")
            if not upload.success:
                raise RuntimeError("Fish Audio 语音预览保存失败，请检查本地存储权限")
            results[voice.id] = upload.url
            print(f"{voice.id}: 已生成 {result.duration:.1f} 秒预览", flush=True)
    finally:
        close = getattr(service, "close", None)
        if close is not None:
            await close()
    return results


async def main():
    parser = argparse.ArgumentParser(description="生成 Fish Audio 在线语音 CLI 音色预览")
    parser.add_argument("--provider", default="fish_speech", choices=["fish_speech", "fish_audio"])
    parser.add_argument("--force", action="store_true", help="强制重新生成已有预览")
    args = parser.parse_args()
    for voice_id, url in (await generate_and_save_previews(force=args.force)).items():
        print(f"{voice_id}: {url}")


if __name__ == "__main__":
    asyncio.run(main())
