# tests/api/test_feedback.py
import pytest
from unittest.mock import AsyncMock, MagicMock


def test_feedback_type_enum():
    """Test FeedbackType enum values."""
    from moana.models.feedback import FeedbackType

    assert FeedbackType.BUG.value == "bug"
    assert FeedbackType.CONTENT.value == "content"
    assert FeedbackType.SUGGEST.value == "suggest"
    assert FeedbackType.OTHER.value == "other"


def test_feedback_status_enum():
    """Test FeedbackStatus enum values."""
    from moana.models.feedback import FeedbackStatus

    assert FeedbackStatus.PENDING.value == "pending"
    assert FeedbackStatus.REVIEWED.value == "reviewed"
    assert FeedbackStatus.RESOLVED.value == "resolved"


def test_feedback_model_creation():
    """Test Feedback model creation."""
    from moana.models.feedback import Feedback, FeedbackType, FeedbackStatus

    feedback = Feedback(
        user_id="user123",
        type=FeedbackType.BUG,
        content="This is a bug report with enough characters to pass validation.",
        contact="user@example.com",
    )

    assert feedback.id is not None
    assert feedback.user_id == "user123"
    assert feedback.type == FeedbackType.BUG
    assert feedback.content.startswith("This is a bug")
    assert feedback.contact == "user@example.com"
    assert feedback.status == FeedbackStatus.PENDING


def test_feedback_model_optional_fields():
    """Test Feedback model with optional fields."""
    from moana.models.feedback import Feedback, FeedbackType

    feedback = Feedback(
        type=FeedbackType.SUGGEST,
        content="This is a suggestion with enough characters to pass validation.",
    )

    assert feedback.id is not None
    assert feedback.user_id is None
    assert feedback.contact is None


def test_feedback_request_schema():
    """Test FeedbackRequest schema validation."""
    from moana.routers.feedback import FeedbackRequest
    from moana.models.feedback import FeedbackType

    request = FeedbackRequest(
        type=FeedbackType.BUG,
        content="This is a bug report with enough characters.",
        contact="user@example.com",
    )

    assert request.type == FeedbackType.BUG
    assert "bug report" in request.content
    assert request.contact == "user@example.com"


def test_feedback_request_schema_min_length():
    """Test FeedbackRequest content minimum length."""
    from moana.routers.feedback import FeedbackRequest
    from moana.models.feedback import FeedbackType
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        FeedbackRequest(
            type=FeedbackType.BUG,
            content="short",  # Less than 10 characters
        )

    assert "content" in str(exc_info.value)


def test_feedback_request_schema_max_length():
    """Test FeedbackRequest content maximum length."""
    from moana.routers.feedback import FeedbackRequest
    from moana.models.feedback import FeedbackType
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        FeedbackRequest(
            type=FeedbackType.BUG,
            content="x" * 501,  # More than 500 characters
        )

    assert "content" in str(exc_info.value)


def test_feedback_response_schema():
    """Test FeedbackResponse schema."""
    from moana.routers.feedback import FeedbackResponse

    response = FeedbackResponse(
        feedback_id="fb123",
        message="Thank you for your feedback",
    )

    assert response.feedback_id == "fb123"
    assert response.message == "Thank you for your feedback"


def test_feedback_router_exists():
    """Test feedback router can be imported."""
    from moana.routers.feedback import router

    assert router is not None


def test_get_current_user_optional_exists():
    """Test get_current_user_optional function exists."""
    from moana.routers.auth import get_current_user_optional

    assert get_current_user_optional is not None


@pytest.mark.asyncio
async def test_get_current_user_optional_no_auth():
    """Test get_current_user_optional returns None without auth."""
    from moana.routers.auth import get_current_user_optional

    mock_db = AsyncMock()

    result = await get_current_user_optional(authorization=None, db=mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_submit_feedback_anonymous():
    """Test submitting feedback as anonymous user."""
    from moana.routers.feedback import submit_feedback, FeedbackRequest
    from moana.models.feedback import FeedbackType

    mock_db = AsyncMock()

    request = FeedbackRequest(
        type=FeedbackType.SUGGEST,
        content="This is a great suggestion for improvement.",
    )

    response = await submit_feedback(
        request=request,
        db=mock_db,
        current_user=None,
    )

    assert response.feedback_id is not None
    assert response.message == "感谢您的反馈"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_submit_feedback_authenticated():
    """Test submitting feedback as authenticated user."""
    from moana.routers.feedback import submit_feedback, FeedbackRequest
    from moana.models.feedback import FeedbackType
    from moana.models.user import User

    mock_db = AsyncMock()
    mock_user = MagicMock(spec=User)
    mock_user.id = "user123"

    request = FeedbackRequest(
        type=FeedbackType.BUG,
        content="This is a bug report from an authenticated user.",
        contact="user@example.com",
    )

    response = await submit_feedback(
        request=request,
        db=mock_db,
        current_user=mock_user,
    )

    assert response.feedback_id is not None
    assert response.message == "感谢您的反馈"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_feedback_model_exported():
    """Test Feedback model is exported from models package."""
    from moana.models import Feedback, FeedbackType, FeedbackStatus

    assert Feedback is not None
    assert FeedbackType is not None
    assert FeedbackStatus is not None
