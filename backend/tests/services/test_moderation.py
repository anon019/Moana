# tests/services/test_moderation.py
import pytest


def test_moderation_imports():
    """Test moderation service can be imported."""
    from moana.services.moderation import (
        ModerationService,
        ModerationResult,
        ContentModerationRequest,
        AliyunModerationService,
    )
    assert ModerationService is not None
    assert ModerationResult is not None
    assert ContentModerationRequest is not None
    assert AliyunModerationService is not None


def test_moderation_result():
    """Test ModerationResult dataclass."""
    from moana.services.moderation.base import ModerationResult, ModerationCategory

    result = ModerationResult(
        is_safe=True,
        categories=[ModerationCategory.SAFE],
        confidence=0.99,
    )

    assert result.is_safe is True
    assert len(result.categories) == 1
    assert result.confidence == 0.99

    result_dict = result.to_dict()
    assert result_dict["is_safe"] is True
    assert "safe" in result_dict["categories"]


def test_content_moderation_request():
    """Test ContentModerationRequest dataclass."""
    from moana.services.moderation.base import ContentModerationRequest

    request = ContentModerationRequest(
        text="Hello world",
        image_url="https://example.com/image.png",
    )

    assert request.text == "Hello world"
    assert request.image_url == "https://example.com/image.png"
    assert request.audio_url is None


@pytest.mark.asyncio
async def test_aliyun_moderate_text_not_configured():
    """Test Aliyun moderation with no credentials."""
    from moana.services.moderation import AliyunModerationService

    service = AliyunModerationService()
    result = await service.moderate_text("Test content")

    # Should return safe when not configured
    assert result.is_safe is True


@pytest.mark.asyncio
async def test_aliyun_moderate_image_not_configured():
    """Test Aliyun image moderation with no credentials."""
    from moana.services.moderation import AliyunModerationService

    service = AliyunModerationService()
    result = await service.moderate_image("https://example.com/test.png")

    assert result.is_safe is True


def test_review_status_enum():
    """Test ReviewStatus enum exists in models."""
    from moana.models import ReviewStatus

    assert ReviewStatus.PENDING.value == "pending"
    assert ReviewStatus.APPROVED.value == "approved"
    assert ReviewStatus.REJECTED.value == "rejected"


def test_review_agent_import():
    """Test ReviewAgent can be imported."""
    from moana.agents import ReviewAgent

    assert ReviewAgent is not None
