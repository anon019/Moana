"""Tests for theme configuration module."""
import pytest


def test_theme_dataclass_exists():
    """Test Theme dataclass can be imported."""
    from moana.themes import Theme

    theme = Theme(
        id="brush_teeth",
        name="刷牙",
        category="habit",
        subcategory="生活自理",
        age_range=(12, 48),
        keywords=["刷牙", "牙齿"],
        default_story_hint="小动物学刷牙",
        default_song_hint="欢快的刷牙歌",
    )
    assert theme.id == "brush_teeth"
    assert theme.category == "habit"


def test_theme_registry_exists():
    """Test THEME_REGISTRY contains themes."""
    from moana.themes import THEME_REGISTRY

    assert len(THEME_REGISTRY) > 0
    assert "brush_teeth" in THEME_REGISTRY


def test_get_themes_by_category():
    """Test filtering themes by category."""
    from moana.themes import get_themes_by_category

    habit_themes = get_themes_by_category("habit")
    assert len(habit_themes) > 0
    assert all(t.category == "habit" for t in habit_themes)

    cognition_themes = get_themes_by_category("cognition")
    assert len(cognition_themes) > 0
    assert all(t.category == "cognition" for t in cognition_themes)


def test_get_themes_for_age():
    """Test filtering themes by age."""
    from moana.themes import get_themes_for_age

    themes_24m = get_themes_for_age(24)
    assert len(themes_24m) > 0
    for theme in themes_24m:
        assert theme.age_range[0] <= 24 <= theme.age_range[1]


def test_find_theme_by_keyword():
    """Test finding theme by keyword."""
    from moana.themes import find_theme_by_keyword

    theme = find_theme_by_keyword("牙齿")
    assert theme is not None
    assert "牙" in theme.name or "牙齿" in theme.keywords


def test_get_all_themes():
    """Test getting all themes."""
    from moana.themes import get_all_themes

    themes = get_all_themes()
    assert len(themes) >= 10  # 至少10个主题
