# tests/api/test_content.py
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    from moana.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_picture_book_endpoint():
    """Test picture book generation endpoint exists."""
    from moana.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Just check endpoint exists (will fail validation without body)
        response = await client.post("/api/v1/content/picture-book")
        # Should be 422 (validation error) not 404
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_nursery_rhyme_endpoint():
    """Test nursery rhyme generation endpoint exists."""
    from moana.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/content/nursery-rhyme")
        # Should be 422 (validation error) not 404
        assert response.status_code == 422
