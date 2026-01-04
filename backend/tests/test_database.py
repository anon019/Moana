import pytest


def test_database_engine_creation():
    """Test database engine can be created."""
    from moana.database import get_engine

    engine = get_engine()
    assert engine is not None


@pytest.mark.asyncio
async def test_async_session():
    """Test async session can be created."""
    from moana.database import get_async_session

    async for session in get_async_session():
        assert session is not None
        break
