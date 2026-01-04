"""Tests for first-frame API."""
import pytest
from httpx import AsyncClient, ASGITransport
from moana.main import app


class TestFirstFrameAPI:
    """Test first-frame generation API."""

    @pytest.fixture
    def client(self):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_generate_first_frame_success(self, client):
        """Test successful first frame generation."""
        response = await client.post(
            "/api/v1/content/video/first-frame",
            json={
                "prompt": "一只可爱的小兔子在花园里吃胡萝卜",
                "child_name": "小明",
                "art_style": "storybook",
                "aspect_ratio": "16:9",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert "prompt_enhanced" in data
        assert data["image_url"].startswith("https://")

    @pytest.mark.asyncio
    async def test_generate_first_frame_validation(self, client):
        """Test request validation."""
        # Missing required field
        response = await client.post(
            "/api/v1/content/video/first-frame",
            json={"prompt": "test"},  # Missing child_name
        )

        assert response.status_code == 422  # Validation error
