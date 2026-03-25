# Moana

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
- `GEMINI_IMAGE_MODEL`
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
- The default image generation path uses Gemini with `GEMINI_IMAGE_MODEL=gemini-3.1-flash-image-preview` (documented in the codebase as the Nano Banana image model).
- This directory is the backend codebase. In the public monorepo, it is synced into `backend/`.
- The public version intentionally keeps runtime URLs configurable and avoids hardcoded deployment-specific domains.
