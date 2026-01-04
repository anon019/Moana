"""Tests for smart mode picture book API."""
import pytest
from httpx import AsyncClient, ASGITransport
from moana.main import app


class TestSmartPictureBookAPI:
    """Test smart mode for picture book."""

    @pytest.fixture
    def client(self):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_smart_mode_requires_custom_prompt(self, client):
        """Test that smart mode requires custom_prompt."""
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "smart",
                # Missing custom_prompt
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "custom_prompt" in str(data).lower() or "智能创作" in str(data)

    @pytest.mark.asyncio
    async def test_preset_mode_requires_theme_fields(self, client):
        """Test that preset mode requires theme_topic and theme_category."""
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "preset",
                # Missing theme_topic and theme_category
            },
        )

        assert response.status_code == 422
        data = response.json()
        # Should complain about missing theme fields
        assert "theme" in str(data).lower() or "预设" in str(data)

    @pytest.mark.asyncio
    async def test_smart_mode_success(self, client):
        """Test successful smart mode creation."""
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "smart",
                "custom_prompt": "宝宝最近不爱吃蔬菜，帮我做一个关于吃蔬菜的故事",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_preset_mode_success(self, client):
        """Test successful preset mode creation."""
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "preset",
                "theme_topic": "吃蔬菜",
                "theme_category": "habit",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_default_mode_is_preset(self, client):
        """Test that default mode is preset."""
        # Without creation_mode, should default to preset
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "theme_topic": "刷牙",
                "theme_category": "habit",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
