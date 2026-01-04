import os
import pytest


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear settings cache between tests to prevent pollution."""
    from moana.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_loads_from_env():
    """Test that settings can load from environment variables."""
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost/test"
    os.environ["ANTHROPIC_API_KEY"] = "test_key"

    from moana.config import get_settings

    settings = get_settings()
    assert settings.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert settings.anthropic_api_key == "test_key"


def test_settings_singleton():
    """Test that get_settings returns cached instance."""
    from moana.config import get_settings

    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_music_provider_config():
    """Test music provider configuration."""
    import os
    os.environ["MUSIC_PROVIDER"] = "minimax"
    os.environ["MINIMAX_API_KEY"] = "test_minimax_key"

    from moana.config import get_settings
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.music_provider == "minimax"
    assert settings.minimax_api_key == "test_minimax_key"
    assert settings.minimax_music_model == "music-2.0"
