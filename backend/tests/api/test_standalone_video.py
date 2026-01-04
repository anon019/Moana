"""Tests for standalone video API."""
import pytest
from httpx import AsyncClient, ASGITransport
from moana.main import app


class TestStandaloneVideoAPI:
    """Test standalone video API."""

    @pytest.fixture
    def client(self):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_create_standalone_video_task(self, client):
        """Test creating standalone video task."""
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "小兔子在花园里开心地吃胡萝卜",
                "generate_first_frame": True,
                "duration_seconds": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_id"].startswith("standalone_video_")
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_validation_error(self, client):
        """Test request validation."""
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                # Missing required fields
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_with_first_frame_url(self, client):
        """Test creating video with provided first frame URL."""
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "小兔子在花园里开心地玩耍",
                "first_frame_url": "https://example.com/my-frame.png",
                "generate_first_frame": False,
                "duration_seconds": 6,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_id"].startswith("standalone_video_")

    @pytest.mark.asyncio
    async def test_validation_duration_bounds(self, client):
        """Test duration validation."""
        # Duration too short
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "测试",
                "duration_seconds": 3,  # Below minimum
            },
        )
        assert response.status_code == 422

        # Duration too long
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "测试",
                "duration_seconds": 10,  # Above maximum
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_validation_age_bounds(self, client):
        """Test age validation."""
        # Age too young
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 6,  # Below minimum
                "custom_prompt": "测试",
            },
        )
        assert response.status_code == 422

        # Age too old
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 100,  # Above maximum
                "custom_prompt": "测试",
            },
        )
        assert response.status_code == 422
