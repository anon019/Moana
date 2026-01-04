"""Tests for Veo prompt enhancer."""
import pytest
from moana.services.video.prompt_enhancer import (
    STYLE_KEYWORDS,
    CAMERA_MOVEMENTS,
    MOTION_INTENSITIES,
    build_negative_prompt,
    enhance_prompt_with_style,
)


class TestStyleKeywords:
    """Test style keyword definitions."""

    def test_style_keywords_exist(self):
        """Should have predefined style keywords."""
        assert len(STYLE_KEYWORDS) >= 5
        assert "cartoon" in STYLE_KEYWORDS
        assert "watercolor" in STYLE_KEYWORDS

    def test_camera_movements_exist(self):
        """Should have predefined camera movements."""
        assert len(CAMERA_MOVEMENTS) >= 5
        assert "static" in CAMERA_MOVEMENTS
        assert "tracking" in CAMERA_MOVEMENTS

    def test_motion_intensities_exist(self):
        """Should have motion intensity adverbs."""
        assert "subtle" in MOTION_INTENSITIES
        assert "dynamic" in MOTION_INTENSITIES


class TestBuildNegativePrompt:
    """Test negative prompt building."""

    def test_build_negative_prompt_basic(self):
        """Should build negative prompt from presets."""
        result = build_negative_prompt(["realistic", "blur"])
        assert "realistic" in result.lower()
        assert "blur" in result.lower()

    def test_build_negative_prompt_with_custom(self):
        """Should include custom negative prompt."""
        result = build_negative_prompt(["realistic"], custom="no cats")
        assert "realistic" in result.lower()
        assert "no cats" in result.lower()

    def test_build_negative_prompt_with_style(self):
        """Should add style-specific negatives for style preservation."""
        result = build_negative_prompt([], style_to_preserve="watercolor")
        assert "3d" in result.lower() or "realistic" in result.lower()


class TestEnhancePrompt:
    """Test prompt enhancement."""

    def test_enhance_prompt_adds_style(self):
        """Should add style keywords to prompt."""
        result = enhance_prompt_with_style(
            prompt="A rabbit dancing",
            detected_style="watercolor",
            camera_movement="slow_zoom",
            motion_intensity="normal",
        )
        assert "watercolor" in result.lower()
        assert "rabbit" in result.lower()

    def test_enhance_prompt_adds_camera(self):
        """Should add camera movement."""
        result = enhance_prompt_with_style(
            prompt="A rabbit dancing",
            detected_style="cartoon",
            camera_movement="tracking",
            motion_intensity="dynamic",
        )
        assert "tracking" in result.lower() or "follow" in result.lower()

    def test_enhance_prompt_adds_motion_intensity(self):
        """Should add motion intensity adverbs to prompt."""
        # Test subtle intensity
        result_subtle = enhance_prompt_with_style(
            prompt="A bird flying",
            motion_intensity="subtle",
        )
        assert "gently" in result_subtle.lower()

        # Test slow intensity
        result_slow = enhance_prompt_with_style(
            prompt="A bird flying",
            motion_intensity="slow",
        )
        assert "slowly" in result_slow.lower()

        # Test dynamic intensity
        result_dynamic = enhance_prompt_with_style(
            prompt="A bird flying",
            motion_intensity="dynamic",
        )
        assert "quickly" in result_dynamic.lower()

        # Test normal intensity
        result_normal = enhance_prompt_with_style(
            prompt="A bird flying",
            motion_intensity="normal",
        )
        assert "naturally" in result_normal.lower()


class TestVeoPromptEnhancer:
    """Test the full VeoPromptEnhancer class."""

    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance."""
        from moana.services.video.prompt_enhancer import VeoPromptEnhancer
        return VeoPromptEnhancer()

    def test_enhancer_has_enhance_method(self, enhancer):
        """Enhancer should have async enhance method."""
        assert hasattr(enhancer, "enhance")
        import asyncio
        assert asyncio.iscoroutinefunction(enhancer.enhance)

    def test_enhancer_has_analyze_style_method(self, enhancer):
        """Enhancer should have analyze_style method."""
        assert hasattr(enhancer, "analyze_image_style")

    @pytest.mark.asyncio
    async def test_enhance_returns_enhanced_result(self, enhancer):
        """enhance() should return EnhancedPrompt dataclass."""
        from moana.services.video.prompt_enhancer import EnhancedPrompt
        # Use simple mode without LLM
        result = await enhancer.enhance(
            prompt="小兔子跳舞",
            use_llm=False,
            detected_style="cartoon",
            motion_mode="normal",
        )
        assert isinstance(result, EnhancedPrompt)
        assert result.enhanced_prompt != ""
        assert result.negative_prompt != ""
