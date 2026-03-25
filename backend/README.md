# Moana

AI-native early childhood education content generation system

## Overview

Moana is an intelligent backend service for early childhood education content generation. It produces personalized picture books, nursery rhymes, and educational videos, and also records play history, learning interactions, and learning statistics for children.

## Features

- Personalized picture book generation
- Nursery rhyme generation with TTS support
- Educational video generation
- Interactive learning records and play tracking
- Learning statistics based on play history and interaction data
- Theme-based content for early childhood learning

## Requirements

- Python 3.11+
- PostgreSQL

## Installation

1. Install dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

2. Create environment configuration from the example file:

   ```bash
   cp .env.example .env
   ```

3. Update the required provider and database settings in `.env`.

Key settings include:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `IMAGE_PROVIDER`
- `TTS_PROVIDER`
- `MUSIC_PROVIDER`
- `VIDEO_PROVIDER`

## Database Migrations

Apply the latest schema before starting the server:

```bash
alembic upgrade head
```

Recent migrations include play history and interaction tracking tables used by the learning flow.

## Run the Backend

```bash
uvicorn moana.main:app --reload
```

## Testing

Run the test suite:

```bash
pytest
```

## Project Structure

- `src/moana/`: application source code
- `alembic/`: database migrations
- `tests/`: automated tests
- `web/`: frontend assets used by the backend project

## Notes

- Keep secrets in local `.env` files only. Do not commit provider keys or private data.
- This directory is the backend codebase. In the public monorepo, it is published under `backend/`.
