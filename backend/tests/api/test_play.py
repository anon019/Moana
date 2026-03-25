import asyncio
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from moana.api.play import router as play_router
from moana.database import get_db
from moana.models.base import Base
from moana.models.child import Child
from moana.models.content import Content, ContentType
from moana.models.play_history import InteractionRecord, PlayHistory
from moana.models.user import User
from moana.routers.auth import get_current_user

USER_ID = "user-test"
CHILD_ID = "child-test"
BOOK_1_ID = "content-book-1"
BOOK_2_ID = "content-book-2"
BOOK_3_ID = "content-book-3"
SONG_ID = "content-song-1"


async def _prepare_db(session_factory, engine):
    tables = [
        User.__table__,
        Child.__table__,
        Content.__table__,
        PlayHistory.__table__,
        InteractionRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=tables))

    async with session_factory() as session:
        session.add(User(id=USER_ID, openid="openid-test", nickname="Tester"))
        session.add(
            Child(
                id=CHILD_ID,
                name="Kid",
                birth_date=date(2023, 1, 1),
                parent_id=USER_ID,
            )
        )
        session.add_all(
            [
                Content(
                    id=BOOK_1_ID,
                    child_id=CHILD_ID,
                    title="Book 1",
                    content_type=ContentType.PICTURE_BOOK,
                    theme_category="habit",
                    theme_topic="brushing teeth",
                    content_data={"pages": [{}, {}, {}, {}, {}]},
                ),
                Content(
                    id=BOOK_2_ID,
                    child_id=CHILD_ID,
                    title="Book 2",
                    content_type=ContentType.PICTURE_BOOK,
                    theme_category="cognition",
                    theme_topic="colors",
                    content_data={"pages": [{}, {}, {}]},
                ),
                Content(
                    id=BOOK_3_ID,
                    child_id=CHILD_ID,
                    title="Book 3",
                    content_type=ContentType.PICTURE_BOOK,
                    theme_category="cognition",
                    theme_topic="animals",
                    content_data={"pages": [{}, {}]},
                ),
                Content(
                    id=SONG_ID,
                    child_id=CHILD_ID,
                    title="Song 1",
                    content_type=ContentType.NURSERY_RHYME,
                    theme_category="habit",
                    theme_topic="bedtime",
                    content_data={"sections": ["verse"]},
                ),
            ]
        )
        await session.commit()


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "play-test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    asyncio.run(_prepare_db(session_factory, engine))

    app = FastAPI()
    app.include_router(play_router, prefix="/api/v1/play")

    async def override_get_db():
        async with session_factory() as session:
            yield session

    async def override_current_user():
        return User(id=USER_ID, openid="openid-test", nickname="Tester")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


def test_start_progress_and_complete_flow(client):
    start = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": BOOK_1_ID,
            "content_type": "picture_book",
            "total_pages": 5,
        },
    )
    assert start.status_code == 200
    started = start.json()
    assert started["current_page"] == 1
    assert started["completion_rate"] == 0.0
    assert started["is_resumed"] is False

    progress = client.post(
        "/api/v1/play/progress",
        json={
            "play_history_id": started["play_history_id"],
            "current_page": 3,
        },
    )
    assert progress.status_code == 200
    assert progress.json()["completion_rate"] == 0.6

    complete = client.post(
        "/api/v1/play/complete",
        json={"play_history_id": started["play_history_id"]},
    )
    assert complete.status_code == 200
    completed = complete.json()
    assert completed["completed_at"]
    assert completed["total_time_seconds"] >= 0


def test_start_play_resumes_existing_session(client):
    first = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": BOOK_2_ID,
            "content_type": "picture_book",
            "total_pages": 3,
        },
    )
    play_history_id = first.json()["play_history_id"]

    client.post(
        "/api/v1/play/progress",
        json={
            "play_history_id": play_history_id,
            "current_page": 2,
        },
    )

    resumed = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": BOOK_2_ID,
            "content_type": "picture_book",
            "total_pages": 3,
        },
    )
    assert resumed.status_code == 200
    payload = resumed.json()
    assert payload["is_resumed"] is True
    assert payload["current_page"] == 2


def test_history_cursor_pagination_keeps_total_count(client):
    for content_id, total_pages in [(BOOK_1_ID, 5), (BOOK_2_ID, 3), (BOOK_3_ID, 2)]:
        response = client.post(
            "/api/v1/play/start",
            json={
                "child_id": CHILD_ID,
                "content_id": content_id,
                "content_type": "picture_book",
                "total_pages": total_pages,
            },
        )
        assert response.status_code == 200

    first_page = client.get(f"/api/v1/play/history/{CHILD_ID}", params={"limit": 2})
    assert first_page.status_code == 200
    first_payload = first_page.json()
    assert first_payload["total"] == 3
    assert len(first_payload["items"]) == 2
    assert first_payload["has_more"] is True
    assert first_payload["next_cursor"]

    second_page = client.get(
        f"/api/v1/play/history/{CHILD_ID}",
        params={"limit": 2, "cursor": first_payload["next_cursor"]},
    )
    assert second_page.status_code == 200
    second_payload = second_page.json()
    assert second_payload["total"] == 3
    assert len(second_payload["items"]) == 1
    assert second_payload["has_more"] is False


def test_submit_interaction_rejects_page_beyond_total_pages(client):
    start = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": BOOK_3_ID,
            "content_type": "picture_book",
            "total_pages": 2,
        },
    )
    play_history_id = start.json()["play_history_id"]

    response = client.post(
        "/api/v1/play/interaction",
        json={
            "play_history_id": play_history_id,
            "page_num": 3,
            "question_type": "choice",
            "is_correct": True,
            "attempts": 1,
            "time_spent_ms": 1500,
        },
    )
    assert response.status_code == 400
    assert "page" in response.json()["detail"].lower()


def test_learning_stats_reports_books_and_songs(client):
    book = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": BOOK_1_ID,
            "content_type": "picture_book",
            "total_pages": 5,
        },
    )
    book_id = book.json()["play_history_id"]
    client.post(
        "/api/v1/play/complete",
        json={"play_history_id": book_id},
    )

    song = client.post(
        "/api/v1/play/start",
        json={
            "child_id": CHILD_ID,
            "content_id": SONG_ID,
            "content_type": "nursery_rhyme",
            "total_pages": 1,
        },
    )
    assert song.status_code == 200

    stats = client.get(f"/api/v1/play/learning-stats/{CHILD_ID}")
    assert stats.status_code == 200
    payload = stats.json()
    assert payload["period"]["days"] == 7
    assert payload["summary"]["total_books"] >= 1
    assert payload["summary"]["total_songs"] >= 1
    assert isinstance(payload["daily_activity"], list)
    assert isinstance(payload["top_themes"], list)
