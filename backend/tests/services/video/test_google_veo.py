"""Tests for enhanced Google Veo service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestEnhancedGoogleVeoService:
    """Test enhanced Veo service features."""

    def test_generate_accepts_new_parameters(self):
        """generate() should accept new enhancement parameters."""
        from moana.services.video.google_veo import GoogleVeoService
        import inspect

        sig = inspect.signature(GoogleVeoService.generate)
        params = sig.parameters

        # Check new parameters exist
        assert "scene_template" in params
        assert "character_ids" in params
        assert "reference_images" in params
        assert "auto_enhance_prompt" in params
        assert "negative_prompt" in params

    def test_service_has_enhancer(self):
        """Service should have prompt enhancer."""
        with patch("moana.services.video.google_veo.genai"):
            from moana.services.video.google_veo import GoogleVeoService
            service = GoogleVeoService()
            assert hasattr(service, "_prompt_enhancer")

    def test_service_has_reference_manager(self):
        """Service should have reference manager."""
        with patch("moana.services.video.google_veo.genai"):
            from moana.services.video.google_veo import GoogleVeoService
            service = GoogleVeoService()
            assert hasattr(service, "_reference_manager")
