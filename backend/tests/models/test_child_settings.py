"""Tests for ChildSettings model."""
import uuid

import pytest


def test_child_settings_model_creation():
    """Test ChildSettings model can be created."""
    from moana.models.child_settings import ChildSettings

    settings = ChildSettings(
        id=uuid.uuid4(),
        child_id=uuid.uuid4(),
        daily_limit_minutes=60,
        session_limit_minutes=20,
        rest_reminder_enabled=True,
    )

    assert settings.daily_limit_minutes == 60
    assert settings.session_limit_minutes == 20
    assert settings.rest_reminder_enabled is True


def test_child_settings_defaults():
    """Test ChildSettings default values."""
    from moana.models.child_settings import ChildSettings

    defaults = ChildSettings.get_defaults()

    assert defaults["daily_limit_minutes"] == 60
    assert defaults["session_limit_minutes"] == 20
    assert defaults["rest_reminder_enabled"] is True


def test_child_settings_custom_values():
    """Test ChildSettings with custom values."""
    from moana.models.child_settings import ChildSettings

    settings = ChildSettings(
        id=uuid.uuid4(),
        child_id=uuid.uuid4(),
        daily_limit_minutes=30,
        session_limit_minutes=10,
        rest_reminder_enabled=False,
    )

    assert settings.daily_limit_minutes == 30
    assert settings.session_limit_minutes == 10
    assert settings.rest_reminder_enabled is False
