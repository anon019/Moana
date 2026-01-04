"""Tests for video configuration endpoint."""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_get_video_config_returns_all_options():
    """Test that video config endpoint returns all expected configuration options."""
    from moana.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/content/video/config")

    assert response.status_code == 200
    data = response.json()

    # Check all required top-level keys
    assert "scene_templates" in data
    assert "durations" in data
    assert "resolutions" in data
    assert "negative_prompt_presets" in data
    assert "enhancement_options" in data

    # Validate scene_templates structure
    assert isinstance(data["scene_templates"], list)
    assert len(data["scene_templates"]) > 0

    # Check first template has required fields
    first_template = data["scene_templates"][0]
    assert "id" in first_template
    assert "name" in first_template
    assert "description" in first_template
    assert "duration" in first_template
    assert "resolution" in first_template

    # Validate durations
    assert isinstance(data["durations"], list)
    durations_values = [d["value"] for d in data["durations"]]
    assert 4 in durations_values
    assert 6 in durations_values
    assert 8 in durations_values

    # Validate resolutions
    assert isinstance(data["resolutions"], list)
    resolution_values = [r["value"] for r in data["resolutions"]]
    assert "720p" in resolution_values
    assert "1080p" in resolution_values

    # Validate negative_prompt_presets
    assert isinstance(data["negative_prompt_presets"], dict)
    assert "blur" in data["negative_prompt_presets"]
    assert "style_change" in data["negative_prompt_presets"]

    # Validate enhancement_options
    assert isinstance(data["enhancement_options"], dict)
    assert "enabled" in data["enhancement_options"]
    assert "styles" in data["enhancement_options"]


@pytest.mark.asyncio
async def test_video_config_structure_matches_frontend_requirements():
    """Test that video config structure matches frontend requirements."""
    from moana.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/content/video/config")

    assert response.status_code == 200
    data = response.json()

    # Scene templates should include specific expected templates
    template_ids = [t["id"] for t in data["scene_templates"]]
    assert "cover_subtle" in template_ids
    assert "character_dialogue" in template_ids
    assert "scene_transition" in template_ids
    assert "action_scene" in template_ids
    assert "emotional_moment" in template_ids

    # Durations should have labels
    for duration in data["durations"]:
        assert "value" in duration
        assert "label" in duration

    # Resolutions should have labels
    for resolution in data["resolutions"]:
        assert "value" in resolution
        assert "label" in resolution

    # Enhancement options should have default value
    assert data["enhancement_options"]["enabled"] is True
    assert isinstance(data["enhancement_options"]["styles"], list)
