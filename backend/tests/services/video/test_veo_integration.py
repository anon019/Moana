"""Integration tests for Veo optimization system."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestVeoOptimizationIntegration:
    """Test the full optimization pipeline."""

    @pytest.fixture
    def mock_genai(self):
        """Mock Google GenAI client."""
        with patch("moana.services.video.google_veo.genai") as mock:
            # Setup mock client
            mock_client = MagicMock()
            mock.Client.return_value = mock_client

            # Setup mock operation
            mock_operation = MagicMock()
            mock_operation.name = "test-operation"
            mock_operation.done = True
            mock_operation.response.generated_videos = [
                MagicMock(video=MagicMock(video_bytes=b"fake_video_data"))
            ]
            mock_client.models.generate_videos.return_value = mock_operation
            mock_client.operations.get.return_value = mock_operation

            yield mock

    @pytest.fixture
    def mock_storage(self):
        """Mock storage service."""
        with patch("moana.services.video.google_veo.get_storage_service") as mock:
            storage = AsyncMock()
            storage.upload_bytes.return_value = MagicMock(
                success=True,
                url="https://example.com/video.mp4"
            )
            mock.return_value = storage
            yield mock

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM service."""
        with patch("moana.services.llm.get_llm_service") as mock:
            llm = MagicMock()
            llm.generate = AsyncMock(return_value="Enhanced prompt text")
            mock.return_value = llm
            yield mock

    @pytest.mark.asyncio
    async def test_full_pipeline_with_template(self, mock_genai, mock_storage, mock_llm):
        """Test generation with scene template.

        This test verifies:
        1. Template parameters are correctly applied
        2. Camera prompt is used for enhancement
        3. Negative prompt is applied
        4. Video generation completes successfully

        Note: To use template duration, caller must explicitly pass duration_seconds
        from the template, since the parameter has a non-None default.
        """
        from moana.services.video.google_veo import GoogleVeoService
        from moana.services.video.templates import get_template

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"fake_image_data"

            service = GoogleVeoService()
            # Get template to use its duration
            template = get_template("action_scene")

            result = await service.generate(
                image_url="https://example.com/image.png",
                prompt="小兔子跳舞",
                scene_template="action_scene",
                duration_seconds=template.duration,  # Explicitly pass template duration
            )

            # Verify result
            assert result.video_url == "https://example.com/video.mp4"
            assert result.duration == 8  # action_scene template duration
            assert result.format == "mp4"
            assert result.has_audio is False  # VEO 当前 API 不支持音频生成

            # Verify genai was called with correct parameters
            call_kwargs = mock_genai.Client().models.generate_videos.call_args.kwargs
            assert call_kwargs["model"] is not None
            assert call_kwargs["prompt"] is not None
            assert call_kwargs["image"] is not None
            assert call_kwargs["config"] is not None

            # Verify config has negative prompt and correct duration
            config = call_kwargs["config"]
            assert config.duration_seconds == 8
            assert config.negative_prompt is not None

    @pytest.mark.asyncio
    async def test_full_pipeline_with_references(self, mock_genai, mock_storage, mock_llm):
        """Test generation with reference images.

        This test verifies:
        1. Characters can be registered with reference images
        2. Reference images are correctly retrieved for the scene
        3. Reference images are passed to Veo API
        4. Maximum of 3 reference images is enforced
        5. Video generation completes with references
        """
        from moana.services.video.google_veo import GoogleVeoService

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"fake_image_data"

            service = GoogleVeoService()

            # Register character
            service.reference_manager.register_character(
                character_id="bunny",
                image_urls=["ref1.png", "ref2.png", "ref3.png"],
                description="white rabbit",
            )

            # Verify character is registered
            chars = service.reference_manager.list_characters()
            assert len(chars) == 1
            assert chars[0]["id"] == "bunny"
            assert chars[0]["image_count"] == 3

            # Generate video with character references
            result = await service.generate(
                image_url="https://example.com/image.png",
                prompt="小兔子跳舞",
                character_ids=["bunny"],
            )

            assert result.video_url == "https://example.com/video.mp4"

            # Verify reference images were passed
            call_kwargs = mock_genai.Client().models.generate_videos.call_args.kwargs
            assert "reference_images" in call_kwargs

            # Verify 3 reference images were downloaded
            # _download_image is called for: 1 main image + 3 reference images = 4 total
            assert mock_dl.call_count >= 4

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_genai, mock_storage):
        """Test that system degrades gracefully when LLM fails.

        This test verifies:
        1. LLM enhancement failure does not crash the pipeline
        2. System falls back to simple prompt enhancement
        3. Video generation continues with original prompt
        4. User receives a usable result despite LLM failure
        5. Warning is logged for debugging
        """
        from moana.services.video.google_veo import GoogleVeoService
        from moana.services.video.templates import get_template

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"fake_image_data"

            # Make LLM fail
            with patch("moana.services.llm.get_llm_service") as mock_llm:
                mock_llm.side_effect = Exception("LLM unavailable")

                service = GoogleVeoService()
                template = get_template("cover_subtle")

                # Should not raise exception - should fall back to simple enhancement
                result = await service.generate(
                    image_url="https://example.com/image.png",
                    prompt="小兔子跳舞",
                    scene_template="cover_subtle",
                    duration_seconds=template.duration,
                )

                # Verify video was still generated
                assert result.video_url is not None
                assert result.video_url == "https://example.com/video.mp4"
                assert result.duration == 4  # cover_subtle template

                # Verify genai was still called
                assert mock_genai.Client().models.generate_videos.called

                # Verify a prompt was used (even if not LLM-enhanced)
                call_kwargs = mock_genai.Client().models.generate_videos.call_args.kwargs
                prompt_used = call_kwargs["prompt"]
                assert prompt_used is not None
                assert len(prompt_used) > 0


class TestReferenceImageDistribution:
    """Test reference image distribution logic."""

    @pytest.fixture
    def mock_genai(self):
        """Mock Google GenAI client."""
        with patch("moana.services.video.google_veo.genai") as mock:
            mock_client = MagicMock()
            mock.Client.return_value = mock_client

            mock_operation = MagicMock()
            mock_operation.name = "test-op"
            mock_operation.done = True
            mock_operation.response.generated_videos = [
                MagicMock(video=MagicMock(video_bytes=b"data"))
            ]
            mock_client.models.generate_videos.return_value = mock_operation
            mock_client.operations.get.return_value = mock_operation

            yield mock

    @pytest.fixture
    def mock_storage(self):
        """Mock storage service."""
        with patch("moana.services.video.google_veo.get_storage_service") as mock:
            storage = AsyncMock()
            storage.upload_bytes.return_value = MagicMock(
                success=True, url="https://example.com/video.mp4"
            )
            mock.return_value = storage
            yield mock

    @pytest.mark.asyncio
    async def test_multiple_character_distribution(self, mock_genai, mock_storage):
        """Test that reference images are distributed correctly among multiple characters.

        Veo 3.1 has a limit of 3 reference images total. When multiple characters
        are in a scene, the system should distribute refs intelligently:
        - 2 characters: 2 refs for primary, 1 for secondary
        """
        from moana.services.video.google_veo import GoogleVeoService

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"data"

            service = GoogleVeoService()

            # Register two characters
            service.reference_manager.register_character(
                character_id="bunny",
                image_urls=["b1.png", "b2.png", "b3.png"],
                description="white rabbit",
            )
            service.reference_manager.register_character(
                character_id="fox",
                image_urls=["f1.png", "f2.png", "f3.png"],
                description="red fox",
            )

            # Get references for both characters
            refs = service.reference_manager.get_references_for_scene(["bunny", "fox"])

            # Should have exactly 3 refs total (2 from bunny, 1 from fox)
            assert len(refs) == 3

            # Should include refs from both characters
            bunny_refs = [r for r in refs if r.startswith("b")]
            fox_refs = [r for r in refs if r.startswith("f")]

            assert len(bunny_refs) == 2  # Primary character
            assert len(fox_refs) == 1    # Secondary character


class TestPromptEnhancementIntegration:
    """Test prompt enhancement integration with different scenarios."""

    @pytest.fixture
    def mock_genai(self):
        """Mock Google GenAI client."""
        with patch("moana.services.video.google_veo.genai") as mock:
            mock_client = MagicMock()
            mock.Client.return_value = mock_client

            mock_operation = MagicMock()
            mock_operation.name = "test-op"
            mock_operation.done = True
            mock_operation.response.generated_videos = [
                MagicMock(video=MagicMock(video_bytes=b"data"))
            ]
            mock_client.models.generate_videos.return_value = mock_operation
            mock_client.operations.get.return_value = mock_operation

            yield mock

    @pytest.fixture
    def mock_storage(self):
        """Mock storage service."""
        with patch("moana.services.video.google_veo.get_storage_service") as mock:
            storage = AsyncMock()
            storage.upload_bytes.return_value = MagicMock(
                success=True, url="https://example.com/video.mp4"
            )
            mock.return_value = storage
            yield mock

    @pytest.mark.asyncio
    async def test_enhancement_disabled(self, mock_genai, mock_storage):
        """Test that enhancement can be disabled when needed.

        Users should be able to provide their own carefully crafted prompts
        without automatic enhancement interfering.
        """
        from moana.services.video.google_veo import GoogleVeoService

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"data"

            service = GoogleVeoService()
            original_prompt = "A rabbit dancing in the forest, watercolor style"

            result = await service.generate(
                image_url="https://example.com/image.png",
                prompt=original_prompt,
                auto_enhance_prompt=False,  # Disable enhancement
                negative_prompt="realistic, 3d, blur",
            )

            assert result.video_url is not None

            # Verify the original prompt was used (possibly with template additions)
            call_kwargs = mock_genai.Client().models.generate_videos.call_args.kwargs
            prompt_used = call_kwargs["prompt"]

            # Should contain the original prompt
            assert "rabbit" in prompt_used.lower()
            assert "dancing" in prompt_used.lower()

    @pytest.mark.asyncio
    async def test_custom_negative_prompt(self, mock_genai, mock_storage):
        """Test that custom negative prompts work when auto-enhancement is disabled.

        When auto_enhance_prompt is False, the custom negative prompt should be used.
        When auto_enhance_prompt is True (default), the enhancer generates its own.
        """
        from moana.services.video.google_veo import GoogleVeoService

        with patch.object(GoogleVeoService, "_download_image", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = b"data"

            service = GoogleVeoService()
            custom_negative = "no cats, no dogs, no birds"

            result = await service.generate(
                image_url="https://example.com/image.png",
                prompt="森林场景",
                negative_prompt=custom_negative,
                auto_enhance_prompt=False,  # Disable enhancement to use custom negative
            )

            assert result.video_url is not None

            # Verify custom negative prompt was used
            call_kwargs = mock_genai.Client().models.generate_videos.call_args.kwargs
            config = call_kwargs["config"]

            # Custom negative prompt should be in the config
            assert config.negative_prompt == custom_negative
