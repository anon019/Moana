"""Tests for video scene templates."""
import pytest
from moana.services.video.templates import (
    SceneTemplate,
    SCENE_TEMPLATES,
    get_template,
    get_default_template,
)


class TestSceneTemplates:
    """Test scene template definitions."""

    def test_template_has_required_fields(self):
        """Each template should have all required fields."""
        required_fields = {
            "name", "description", "duration", "motion_mode",
            "camera_prompt", "negative_prompt", "resolution"
        }
        for template_id, template in SCENE_TEMPLATES.items():
            assert isinstance(template, SceneTemplate)
            for field in required_fields:
                assert hasattr(template, field), f"{template_id} missing {field}"

    def test_get_template_returns_correct_template(self):
        """get_template should return the requested template."""
        template = get_template("cover_subtle")
        assert template is not None
        assert template.name == "封面微动"
        assert template.duration == 4

    def test_get_template_returns_none_for_unknown(self):
        """get_template should return None for unknown template."""
        template = get_template("nonexistent_template")
        assert template is None

    def test_get_default_template(self):
        """get_default_template should return a sensible default."""
        template = get_default_template()
        assert template is not None
        assert template.duration == 6
        assert template.resolution == "720p"

    def test_template_duration_in_valid_range(self):
        """Template duration should be 4, 6, or 8 seconds (Veo limits)."""
        for template_id, template in SCENE_TEMPLATES.items():
            assert template.duration in [4, 6, 8], f"{template_id} has invalid duration"

    def test_template_resolution_valid(self):
        """Template resolution should be 720p or 1080p."""
        for template_id, template in SCENE_TEMPLATES.items():
            assert template.resolution in ["720p", "1080p"], f"{template_id} has invalid resolution"
