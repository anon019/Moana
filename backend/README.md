# Moana


> 2026-10-16 媒体迁移：文本与附图审核使用 ChatGPT/Codex CLI `gpt-6-luna`；图片使用订阅 CLI 内置 GPT Image，请求 `gpt-image-2.5-sunburst`，工具未回传精确底层型号时如实标为 `not_exposed_by_tool`。语音使用 Fish Audio 在线免费 `s2.1-pro-free` CLI（不部署本地模型），视频暂时停用。Gemini、Vertex、Imagen、Veo 全部硬封禁，无自动收费回退。免费政策与验证见 [CLI 与媒体配置](docs/media-cli.md)。

配置 Fish Key：在服务器终端执行 `python3 scripts/configure_fish_audio.py`，隐藏输入并原子保存。默认中文声音来自公开 Fish 音色“配音3”，可通过 `FISH_SPEECH_VOICE_ID` 更换。Fish 官方当前免费期至 2026-11-30；到期后明确停止，需重新核实免费政策，不能自动改成收费型号。

AI-native early childhood education content generation system

## Overview

Moana is the backend codebase for an early childhood education product. It generates personalized picture books, nursery rhymes, and educational videos, and it also records play history, learning interactions, task status, and learning statistics.

This repository directory also contains the `web/` frontend used for backend-side administration and reporting pages. In the public monorepo, this directory is published under `backend/`.

## Features

- Personalized picture book generation
- Nursery rhyme generation with TTS support
- Educational video generation
- Play tracking and interaction records
- Learning statistics based on play history and answers
- Persistent task status storage backed by the database
- Web admin and reporting frontend under `web/`

## Requirements

- Python 3.11+
- PostgreSQL
- 已登录 ChatGPT 的 Codex CLI；图片 worker 使用 Linux systemd
- FFmpeg（音频转码）
- Node.js 18+ (only needed when working on `web/`)

## Installation

1. Install backend dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

2. Create environment configuration from the example file:

   ```bash
   cp .env.example .env
   ```

3. Update the required provider and runtime settings in `.env`.

Key settings include:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `IMAGE_PROVIDER`
- `TTS_PROVIDER`
- `MUSIC_PROVIDER`
- `VIDEO_PROVIDER`
- `CODEX_MODEL` / `CODEX_IMAGE_MODEL`
- `FISH_SPEECH_API_KEY` / `FISH_SPEECH_VOICE_ID`
- `STORAGE_BASE_URL`
- `CALLBACK_BASE_URL`
- `ALLOWED_CORS_ORIGINS`
- `OPENROUTER_SITE_URL`

The committed defaults are local-development-safe values only. Production domains, callback hosts, and provider secrets should be supplied through environment variables, not committed into the repository.

## Database Migrations

Apply the latest schema before starting or restarting the backend:

```bash
alembic upgrade head
```

Recent migrations cover play history, interaction records, task status persistence, and child settings compatibility fields.

## Run the Backend

```bash
uvicorn moana.main:app --reload
```

## Run the Web Frontend

```bash
cd web
npm install
npm run dev
```

The web app uses `VITE_API_URL` when provided. For local development, the Vite proxy falls back to `VITE_DEV_PROXY_TARGET` and then `http://127.0.0.1:8080`.

## Testing

Run the backend test suite:

```bash
pytest
```

For targeted play API regression checks:

```bash
pytest tests/api/test_play.py -q
```

## Project Structure

- `src/moana/`: application source code
- `alembic/`: database migrations
- `tests/`: automated tests
- `web/`: backend-side web frontend

## Notes

- Keep secrets in local `.env` files only. Do not commit provider keys, private data, or production hosts.
- Google Gemini / Vertex AI / Imagen / Veo 请求已在共享客户端入口禁用，包括旧批处理脚本。
- 文本与图片默认使用已登录 ChatGPT 的 Codex CLI，语音默认使用 Fish 免费在线模型，视频暂时停用；失败不会自动切换到收费 API。
- This directory is the backend codebase. In the public monorepo, it is synced into `backend/`.
- The public version intentionally keeps runtime URLs configurable and avoids hardcoded deployment-specific domains.
