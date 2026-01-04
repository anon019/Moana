"""Tests for PlayHistory and InteractionRecord models."""
import uuid
from datetime import datetime, timedelta

import pytest


def test_play_history_model_creation():
    """Test PlayHistory model can be created."""
    from moana.models.play_history import PlayHistory

    history = PlayHistory(
        id=uuid.uuid4(),
        child_id=uuid.uuid4(),
        content_id=uuid.uuid4(),
        content_type="picture_book",
        current_page=1,
        total_pages=10,
        completion_rate=0.1,
        started_at=datetime.now(),
        last_played_at=datetime.now(),
    )

    assert history.content_type == "picture_book"
    assert history.current_page == 1
    assert history.total_pages == 10


def test_play_history_update_progress():
    """Test updating play progress."""
    from moana.models.play_history import PlayHistory

    history = PlayHistory(
        id=uuid.uuid4(),
        child_id=uuid.uuid4(),
        content_id=uuid.uuid4(),
        content_type="picture_book",
        current_page=1,
        total_pages=10,
        completion_rate=0.0,
        started_at=datetime.now(),
        last_played_at=datetime.now(),
    )

    history.update_progress(5)

    assert history.current_page == 5
    assert history.completion_rate == 0.5


def test_play_history_mark_completed():
    """Test marking play as completed."""
    from moana.models.play_history import PlayHistory

    history = PlayHistory(
        id=uuid.uuid4(),
        child_id=uuid.uuid4(),
        content_id=uuid.uuid4(),
        content_type="picture_book",
        current_page=1,
        total_pages=10,
        completion_rate=0.0,
        started_at=datetime.now(),
        last_played_at=datetime.now(),
    )

    history.mark_completed()

    assert history.is_completed
    assert history.completion_rate == 1.0
    assert history.completed_at is not None


def test_interaction_record_creation():
    """Test InteractionRecord model can be created."""
    from moana.models.play_history import InteractionRecord

    record = InteractionRecord(
        id=uuid.uuid4(),
        play_history_id=uuid.uuid4(),
        page_num=3,
        question_type="choice",
        is_correct=True,
        attempts=1,
        time_spent_ms=2500,
        answered_at=datetime.now(),
    )

    assert record.question_type == "choice"
    assert record.is_correct is True
    assert record.attempts == 1
