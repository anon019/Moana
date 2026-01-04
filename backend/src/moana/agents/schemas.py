from typing import Literal

from pydantic import BaseModel, Field


class PageInteraction(BaseModel):
    """Interaction for a picture book page."""
    question_type: str = Field(description="Type: tap_count, choice, tap_object")
    question: str = Field(description="Question to ask the child")
    options: list[str | int] = Field(description="Answer options")
    correct_answer: str | int = Field(description="The correct answer")


class PictureBookPage(BaseModel):
    """A single page of a picture book."""
    page_num: int = Field(description="Page number starting from 1")
    text: str = Field(description="Story text for this page, 1-2 short sentences")
    image_prompt: str = Field(description="Detailed prompt for generating the illustration")
    interaction: PageInteraction | None = Field(
        default=None,
        description="Optional interaction/question for this page"
    )


class PictureBookOutline(BaseModel):
    """Complete picture book structure."""
    title: str = Field(description="Story title including child's name")
    theme_topic: str = Field(description="The theme/topic of the story")
    educational_goal: str = Field(description="What the child will learn")
    pages: list[PictureBookPage] = Field(
        description="List of pages, typically 6-10 pages"
    )
    total_interactions: int = Field(
        description="Number of interactive questions in the book"
    )


class DayPlan(BaseModel):
    """单日学习计划."""
    day: int = Field(ge=1, le=7, description="Day of week, 1-7")
    date: str = Field(description="Date in YYYY-MM-DD format")
    theme: str = Field(description="Theme name")
    category: Literal["habit", "cognition"] = Field(description="Theme category")
    content_types: list[str] = Field(description="Content types to generate")
    story_hint: str = Field(description="Hint for story generation")
    song_hint: str | None = Field(default=None, description="Hint for song generation")


class WeeklyPlan(BaseModel):
    """周学习计划."""
    week_start: str = Field(description="Week start date in YYYY-MM-DD")
    child_id: str = Field(description="Child ID")
    child_name: str = Field(description="Child name")
    age_months: int = Field(description="Child age in months")
    days: list[DayPlan] = Field(description="Daily plans for the week")


class ParsedIntent(BaseModel):
    """解析后的家长意图."""
    intent_type: Literal["ip", "life_event", "interest", "behavior"] = Field(
        description="Type of intent"
    )
    original_input: str = Field(description="Original user input")
    theme: str = Field(description="Extracted theme")
    category: Literal["habit", "cognition"] = Field(description="Theme category")
    educational_goal: str = Field(description="Educational goal")
    story_prompt: str = Field(description="Customized prompt for story generation")
    song_prompt: str | None = Field(default=None, description="Prompt for song")
    video_prompt: str | None = Field(default=None, description="Prompt for video")
    recommended_types: list[str] = Field(description="Recommended content types")
