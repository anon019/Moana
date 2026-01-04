# src/moana/schemas/nursery_rhyme.py
"""Nursery rhyme API request/response schemas.

Implements loose validation strategy:
- Required: child_name, age_months
- Range validated: age_months (12-72), style_weight (0-1), creativity (0-1)
- All other parameters: pass-through without enum validation
"""

from typing import Optional
from pydantic import BaseModel, Field


class NurseryRhymeRequestV2(BaseModel):
    """Request schema for nursery rhyme generation (v2 redesign).

    Supports 31 parameters across 9 categories with loose validation.
    All enum-like parameters are strings to allow frontend flexibility.
    """

    # === Required Parameters (strict validation) ===
    child_name: str = Field(description="Child's name to personalize the song")
    age_months: int = Field(ge=12, le=72, description="Child's age in months")

    # === Mode Parameters ===
    creation_mode: str = Field(default="preset", description="preset or smart")

    # === Theme Parameters (pass-through) ===
    theme_topic: Optional[str] = Field(default=None, description="Theme topic (required for preset mode)")
    theme_category: Optional[str] = Field(default=None, description="Theme category")
    educational_focus: Optional[list[str]] = Field(default=None, description="Educational goals")

    # === Music Style (pass-through) ===
    music_mood: Optional[str] = Field(default=None, description="Music mood/emotion")
    music_genre: Optional[str] = Field(default=None, description="Music genre")
    tempo: Optional[str] = Field(default=None, description="Tempo speed")
    energy_level: Optional[str] = Field(default=None, description="Energy intensity")
    vocal_gender: Optional[str] = Field(default=None, description="Vocal gender")
    vocal_style: Optional[str] = Field(default=None, description="Vocal style")
    instrumental: bool = Field(default=False, description="Instrumental only (no vocals)")

    # === Instruments & Effects (pass-through) ===
    instruments: Optional[list[str]] = Field(default=None, description="Preferred instruments")
    sound_effects: Optional[list[str]] = Field(default=None, description="Sound effects to include")

    # === Language & Culture (pass-through) ===
    language: Optional[str] = Field(default=None, description="Song language")
    cultural_style: Optional[str] = Field(default=None, description="Cultural style")
    lyric_complexity: Optional[str] = Field(default=None, description="Lyric complexity level")

    # === Song Structure (pass-through) ===
    duration_preference: Optional[str] = Field(default=None, description="Preferred duration")
    repetition_level: Optional[str] = Field(default=None, description="Repetition level")
    song_structure: Optional[str] = Field(default=None, description="Song structure type")
    has_actions: bool = Field(default=False, description="Include action instructions")

    # === Personalization (pass-through) ===
    favorite_characters: Optional[list[str]] = Field(default=None, description="Favorite characters")
    favorite_animals: Optional[list[str]] = Field(default=None, description="Favorite animals")
    favorite_colors: Optional[list[str]] = Field(default=None, description="Favorite colors")
    custom_elements: Optional[str] = Field(default=None, description="Custom elements to include")

    # === Suno Advanced Controls (range validated) ===
    negative_tags: Optional[str] = Field(default=None, description="Styles to exclude")
    style_weight: float = Field(default=0.5, ge=0, le=1, description="Style guidance weight")
    creativity: float = Field(default=0.5, ge=0, le=1, description="Creativity/weirdness level")

    # === Smart Mode (pass-through) ===
    custom_prompt: Optional[str] = Field(default=None, description="Custom creative description")
    inspiration_keywords: Optional[list[str]] = Field(default=None, description="Inspiration keywords")

    def to_params_dict(self) -> dict:
        """Convert to dictionary for prompt enhancement."""
        return self.model_dump(exclude_none=True)


class ContentDetailsResponse(BaseModel):
    """Response schema for content details endpoint."""
    content_id: str
    title: str
    created_at: Optional[str] = None

    basic_info: dict
    user_selections: dict
    user_prompt: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    generation_result: dict
    generated_by: dict


class ContentDiagnosticsResponse(BaseModel):
    """Response schema for content diagnostics endpoint."""
    content_id: str
    task_id: Optional[str] = None
    status: str

    timeline: dict
    stage_durations: dict
    raw_request: dict
    prompt_enhancement: dict
    suno_details: dict
    all_tracks: list
    errors: list
    warnings: list
