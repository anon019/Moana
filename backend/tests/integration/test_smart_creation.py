"""Integration tests for smart creation flow.

These tests require actual API keys and external services.
Run with: PYTHONPATH=src pytest tests/integration/ -v -m integration
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock


class TestSmartCreationIntegration:
    """End-to-end tests for smart creation."""

    @pytest.fixture
    def client(self):
        from moana.main import app
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_smart_picture_book_validation(self, client):
        """Test smart mode validation for picture book."""
        # Smart mode without custom_prompt should fail
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

        # Preset mode without theme should fail
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

    @pytest.mark.asyncio
    async def test_smart_nursery_rhyme_validation(self, client):
        """Test smart mode validation for nursery rhyme."""
        # Smart mode without custom_prompt should fail
        response = await client.post(
            "/api/v1/content/nursery-rhyme/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "smart",
                # Missing custom_prompt
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_first_frame_validation(self, client):
        """Test first frame API validation."""
        # Missing child_name should fail
        response = await client.post(
            "/api/v1/content/video/first-frame",
            json={
                "prompt": "可爱的小兔子",
                # Missing child_name
            },
        )
        assert response.status_code == 422

        # Invalid aspect ratio should fail
        response = await client.post(
            "/api/v1/content/video/first-frame",
            json={
                "prompt": "可爱的小兔子",
                "child_name": "小明",
                "aspect_ratio": "invalid",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_standalone_video_validation(self, client):
        """Test standalone video API validation."""
        # Missing required fields should fail
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                # Missing age_months and custom_prompt
            },
        )
        assert response.status_code == 422

        # Invalid duration should fail
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "小兔子玩耍",
                "duration_seconds": 20,  # Max is 8
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_standalone_video_task_creation(self, client):
        """Test that standalone video task can be created."""
        response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "测试宝贝",
                "age_months": 36,
                "custom_prompt": "一只可爱的小兔子在花园里开心地吃胡萝卜",
                "generate_first_frame": True,
                "duration_seconds": 5,
                "motion_mode": "normal",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_id"].startswith("standalone_video_")
        assert data["status"] == "pending"


class TestSmartCreationWithMocks:
    """Tests with mocked external services."""

    @pytest.fixture
    def client(self):
        from moana.main import app
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_smart_picture_book_flow_mocked(self, client):
        """Test smart picture book creation with mocked analyzer."""
        # Patch where the class is imported FROM (moana.services.smart.__init__)
        # NOT where it's defined (moana.services.smart.prompt_analyzer)
        with patch("moana.services.smart.SmartPromptAnalyzer") as MockAnalyzer:
            # Setup mock
            mock_analyzer = MagicMock()
            mock_analyzer.analyze = AsyncMock(return_value=MagicMock(
                theme_category="habit",
                theme_topic="吃蔬菜",
                enhanced_prompt="小明学会吃蔬菜的故事",
                educational_goal="培养健康饮食习惯",
                title="小明的蔬菜大冒险",
            ))
            MockAnalyzer.return_value = mock_analyzer

            response = await client.post(
                "/api/v1/content/picture-book/async",
                json={
                    "child_name": "小明",
                    "age_months": 36,
                    "creation_mode": "smart",
                    "custom_prompt": "宝宝不爱吃蔬菜，帮我做一个关于吃蔬菜的故事",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_smart_nursery_rhyme_flow_mocked(self, client):
        """Test smart nursery rhyme creation with mocked analyzer."""
        # Patch where the class is imported FROM (moana.services.smart.__init__)
        with patch("moana.services.smart.SmartPromptAnalyzer") as MockAnalyzer:
            # Setup mock
            mock_analyzer = MagicMock()
            mock_analyzer.analyze = AsyncMock(return_value=MagicMock(
                theme_category="cognition",
                theme_topic="农场动物",
                enhanced_prompt="认识农场小动物的儿歌",
                educational_goal="认识动物",
                title="小明的农场儿歌",
            ))
            MockAnalyzer.return_value = mock_analyzer

            response = await client.post(
                "/api/v1/content/nursery-rhyme/async",
                json={
                    "child_name": "小明",
                    "age_months": 36,
                    "creation_mode": "smart",
                    "custom_prompt": "教宝宝认识农场里的小动物",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data

    @pytest.mark.asyncio
    async def test_first_frame_with_mock(self, client):
        """Test first frame generation with mocked image service."""
        # Patch at the source module where get_image_service is defined
        with patch("moana.services.image.get_image_service") as mock_get_service:
            # Setup mock
            mock_service = MagicMock()
            mock_service.generate = AsyncMock(return_value=MagicMock(
                url="https://test.example.com/image.png",
                revised_prompt="Enhanced prompt for cute bunny",
            ))
            mock_get_service.return_value = mock_service

            response = await client.post(
                "/api/v1/content/video/first-frame",
                json={
                    "prompt": "可爱的小兔子在花园里",
                    "child_name": "小明",
                    "aspect_ratio": "16:9",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["image_url"] == "https://test.example.com/image.png"
            assert "prompt_enhanced" in data


class TestSmartCreationEndToEnd:
    """End-to-end tests requiring real API calls.

    These tests are marked with @pytest.mark.integration and skipped by default.
    Run with: pytest -m integration
    """

    @pytest.fixture
    def client(self):
        from moana.main import app
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API calls - run manually")
    async def test_first_frame_to_video_flow(self, client):
        """Test complete flow: first frame -> standalone video.

        This test makes actual API calls and may take several minutes.
        """
        # Step 1: Generate first frame
        frame_response = await client.post(
            "/api/v1/content/video/first-frame",
            json={
                "prompt": "可爱的小兔子在花园里吃胡萝卜",
                "child_name": "小明",
                "aspect_ratio": "16:9",
            },
        )
        assert frame_response.status_code == 200
        frame_data = frame_response.json()
        frame_url = frame_data["image_url"]
        assert frame_url.startswith("https://")

        # Step 2: Create video with first frame
        video_response = await client.post(
            "/api/v1/content/video/standalone/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "custom_prompt": "小兔子在花园里开心玩耍",
                "first_frame_url": frame_url,
                "generate_first_frame": False,
                "duration_seconds": 5,
            },
        )
        assert video_response.status_code == 200
        task_id = video_response.json()["task_id"]

        # Step 3: Poll status (with timeout)
        for _ in range(60):  # Max 5 minutes
            status_response = await client.get(
                f"/api/v1/content/video/status/{task_id}"
            )
            status = status_response.json()

            if status["status"] == "completed":
                assert "result" in status
                assert "video_url" in status["result"]
                print(f"Video generated: {status['result']['video_url']}")
                return

            if status["status"] == "failed":
                pytest.fail(f"Video generation failed: {status.get('error')}")

            await asyncio.sleep(5)

        pytest.fail("Video generation timed out")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API calls - run manually")
    async def test_smart_picture_book_full_flow(self, client):
        """Test complete smart picture book generation.

        This test makes actual API calls and may take several minutes.
        """
        # Create smart picture book
        response = await client.post(
            "/api/v1/content/picture-book/async",
            json={
                "child_name": "小明",
                "age_months": 36,
                "creation_mode": "smart",
                "custom_prompt": "宝宝最近不爱吃蔬菜，总是把胡萝卜挑出来，帮我做一个关于吃蔬菜的故事",
                "art_style": "storybook",
                "voice_id": "Kore",
            },
        )

        assert response.status_code == 200
        task_id = response.json()["task_id"]

        # Poll for completion
        for _ in range(120):  # Max 10 minutes
            status_response = await client.get(
                f"/api/v1/content/picture-book/status/{task_id}"
            )
            status = status_response.json()

            if status.get("status") == "completed":
                assert "content_id" in status
                print(f"Picture book generated: {status['content_id']}")
                return

            if status.get("status") == "failed":
                pytest.fail(f"Picture book generation failed: {status.get('error')}")

            await asyncio.sleep(5)

        pytest.fail("Picture book generation timed out")
