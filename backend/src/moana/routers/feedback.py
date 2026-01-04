# src/moana/routers/feedback.py
"""Feedback router for user feedback submission."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from moana.database import get_db
from moana.models import User
from moana.models.feedback import Feedback, FeedbackType
from moana.routers.auth import get_current_user_optional

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Request to submit feedback."""

    type: FeedbackType = Field(description="Type of feedback")
    content: str = Field(
        min_length=10,
        max_length=500,
        description="Feedback content (10-500 characters)",
    )
    contact: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional contact information",
    )


class FeedbackResponse(BaseModel):
    """Response for feedback submission."""

    feedback_id: str
    message: str


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> FeedbackResponse:
    """Submit user feedback.

    Accepts feedback from both authenticated and anonymous users.
    """
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        type=request.type,
        content=request.content,
        contact=request.contact,
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackResponse(
        feedback_id=feedback.id,
        message="感谢您的反馈",
    )
