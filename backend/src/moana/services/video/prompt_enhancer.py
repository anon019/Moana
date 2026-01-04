"""Veo prompt enhancement utilities."""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnhancedPrompt:
    """Result of prompt enhancement."""
    enhanced_prompt: str
    negative_prompt: str
    detected_style: str | None = None
    camera_movement: str = "static"
    suggested_duration: int = 6


# Style preservation keywords
STYLE_KEYWORDS: dict[str, str] = {
    "cartoon": "2D cartoon animation style, flat colors, clean lines, cel-shaded",
    "watercolor": "soft watercolor painting style, gentle brush strokes, flowing colors",
    "3d_render": "3D rendered style, smooth surfaces, soft shadows, CGI quality",
    "pixel": "pixel art style, retro game aesthetic, blocky pixels",
    "sketch": "hand-drawn sketch style, pencil texture, artistic lines",
    "oil_painting": "oil painting style, rich textures, visible brushwork",
    "anime": "anime style, large expressive eyes, dynamic poses, Japanese animation",
    "realistic": "photorealistic style, natural lighting, detailed textures",
}

# Camera movement descriptions for Veo
CAMERA_MOVEMENTS: dict[str, str] = {
    "static": "locked static camera, no movement, stable framing",
    "slow_zoom": "slow gentle zoom in, gradual approach",
    "slow_pan": "slow cinematic pan, horizontal movement",
    "tracking": "smooth tracking shot, follow the subject, dynamic camera",
    "orbit": "slow orbit around subject, 360 degree view",
    "aerial": "aerial establishing shot, bird's eye view",
    "handheld": "subtle handheld movement, organic feel",
}

# Motion intensity adverbs
MOTION_INTENSITIES: dict[str, list[str]] = {
    "subtle": ["gently", "slightly", "softly", "barely", "delicately"],
    "slow": ["slowly", "calmly", "peacefully", "quietly", "gracefully"],
    "normal": ["naturally", "smoothly", "steadily", "comfortably"],
    "dynamic": ["quickly", "energetically", "actively", "swiftly", "vigorously"],
}

# Negative prompt presets
NEGATIVE_PRESETS: dict[str, str] = {
    "realistic": "realistic, photographic, photo-real, lifelike",
    "blur": "blur, out of focus, blurry, unfocused",
    "style_change": "style change, inconsistent style, style shift",
    "shaky": "camera shake, jerky motion, unstable, shaky cam",
    "dark": "dark, dimly lit, shadowy, low key lighting",
    "fast": "fast motion, rapid movement, speed blur",
    "distortion": "distortion, warped, stretched, morphing artifacts",
}

# Style-specific negatives to preserve style
STYLE_NEGATIVES: dict[str, str] = {
    "cartoon": "realistic, photographic, 3D render, CGI",
    "watercolor": "sharp edges, flat colors, digital, 3D",
    "3d_render": "2D, flat, hand-drawn, sketchy",
    "pixel": "smooth, high resolution, realistic, 3D",
    "sketch": "polished, digital, 3D render, photographic",
    "anime": "western cartoon, realistic, 3D CGI",
}


def build_negative_prompt(
    presets: list[str],
    custom: str = "",
    style_to_preserve: str | None = None,
) -> str:
    """Build a negative prompt from presets and custom input.

    Args:
        presets: List of preset IDs to include
        custom: Custom negative prompt text
        style_to_preserve: Style name to add style-specific negatives

    Returns:
        Combined negative prompt string
    """
    parts = []

    # Add preset negatives
    for preset_id in presets:
        if preset_id in NEGATIVE_PRESETS:
            parts.append(NEGATIVE_PRESETS[preset_id])

    # Add style-preservation negatives
    if style_to_preserve and style_to_preserve in STYLE_NEGATIVES:
        parts.append(STYLE_NEGATIVES[style_to_preserve])

    # Add custom
    if custom:
        parts.append(custom)

    return ", ".join(parts)


def enhance_prompt_with_style(
    prompt: str,
    detected_style: str | None = None,
    camera_movement: str = "static",
    motion_intensity: str = "normal",
) -> str:
    """Enhance a prompt with style, camera, and motion keywords.

    Args:
        prompt: Original user prompt
        detected_style: Detected art style from image
        camera_movement: Camera movement type
        motion_intensity: Motion intensity level

    Returns:
        Enhanced prompt string
    """
    parts = [prompt]

    # Add style keywords
    if detected_style and detected_style in STYLE_KEYWORDS:
        parts.append(STYLE_KEYWORDS[detected_style])

    # Add camera movement
    if camera_movement and camera_movement in CAMERA_MOVEMENTS:
        parts.append(CAMERA_MOVEMENTS[camera_movement])

    # Add motion intensity adverbs
    if motion_intensity and motion_intensity in MOTION_INTENSITIES:
        adverbs = MOTION_INTENSITIES[motion_intensity]
        # Select first adverb from the intensity level
        if adverbs:
            parts.append(adverbs[0])

    # Add quality keywords
    parts.append("high quality animation, smooth motion, consistent style")

    return ", ".join(parts)


class VeoPromptEnhancer:
    """Intelligent prompt enhancer for Veo 3.1."""

    # Prompt template for LLM enhancement
    ENHANCE_PROMPT_TEMPLATE = """You are a video generation prompt optimizer for Google Veo 3.1.

Given the user's description, create an optimized English prompt following these rules:
1. Describe the SUBJECT clearly (who/what is in the scene)
2. Describe the ACTION with appropriate adverbs (gently, slowly, energetically)
3. Include STYLE keywords to maintain the art style: {style_hint}
4. Include CAMERA movement: {camera_hint}
5. Add ATMOSPHERE and LIGHTING details
6. Keep it under 200 words

User description: {user_prompt}

Output ONLY the enhanced prompt, nothing else."""

    ANALYZE_STYLE_TEMPLATE = """Analyze this image and identify its art style.

Choose ONE primary style from: cartoon, watercolor, 3d_render, pixel, sketch, oil_painting, anime, realistic

Also identify:
- Color palette (warm/cool/pastel/vibrant)
- Line style (clean/sketchy/none)
- Overall mood

Output as JSON:
{{"style": "style_name", "palette": "description", "mood": "description"}}"""

    def __init__(self):
        self._llm_service = None

    def _get_llm_service(self):
        """Lazy load LLM service."""
        if self._llm_service is None:
            from moana.services.llm import get_llm_service
            self._llm_service = get_llm_service()
        return self._llm_service

    async def analyze_image_style(self, image_url: str) -> dict:
        """Analyze image to detect art style using Gemini Vision.

        Args:
            image_url: URL of the image to analyze

        Returns:
            Dict with style, palette, mood
        """
        try:
            llm = self._get_llm_service()
            # Use vision capability
            result = await llm.generate_with_image(
                prompt=self.ANALYZE_STYLE_TEMPLATE,
                image_url=image_url,
            )
            # Parse JSON response
            import json
            return json.loads(result)
        except Exception as e:
            logger.warning(f"Style analysis failed: {e}, using default")
            return {"style": "cartoon", "palette": "warm", "mood": "cheerful"}

    async def enhance(
        self,
        prompt: str,
        use_llm: bool = True,
        detected_style: str | None = None,
        motion_mode: str = "normal",
        camera_movement: str | None = None,
        template_camera_prompt: str | None = None,
    ) -> EnhancedPrompt:
        """Enhance a prompt for optimal Veo generation.

        Args:
            prompt: User's original prompt
            use_llm: Whether to use LLM for enhancement
            detected_style: Pre-detected art style
            motion_mode: Motion intensity mode
            camera_movement: Camera movement type
            template_camera_prompt: Camera prompt from template

        Returns:
            EnhancedPrompt with enhanced prompt and negative prompt
        """
        style = detected_style or "cartoon"
        camera = camera_movement or "static"

        if use_llm:
            try:
                enhanced = await self._enhance_with_llm(
                    prompt, style, camera, template_camera_prompt
                )
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}, falling back to simple")
                enhanced = self._enhance_simple(prompt, style, camera, template_camera_prompt)
        else:
            enhanced = self._enhance_simple(prompt, style, camera, template_camera_prompt)

        # Build negative prompt
        negative = build_negative_prompt(
            presets=["blur", "distortion", "style_change"],
            style_to_preserve=style,
        )

        return EnhancedPrompt(
            enhanced_prompt=enhanced,
            negative_prompt=negative,
            detected_style=style,
            camera_movement=camera,
            suggested_duration=self._suggest_duration(motion_mode),
        )

    async def _enhance_with_llm(
        self,
        prompt: str,
        style: str,
        camera: str,
        template_camera: str | None,
    ) -> str:
        """Enhance prompt using LLM."""
        style_hint = STYLE_KEYWORDS.get(style, "consistent art style")
        camera_hint = template_camera or CAMERA_MOVEMENTS.get(camera, "stable camera")

        llm = self._get_llm_service()
        result = await llm.generate(
            self.ENHANCE_PROMPT_TEMPLATE.format(
                style_hint=style_hint,
                camera_hint=camera_hint,
                user_prompt=prompt,
            )
        )
        return result.strip()

    def _enhance_simple(
        self,
        prompt: str,
        style: str,
        camera: str,
        template_camera: str | None,
    ) -> str:
        """Simple enhancement without LLM."""
        return enhance_prompt_with_style(
            prompt=prompt,
            detected_style=style,
            camera_movement=camera,
            motion_intensity="normal",
        )

    def _suggest_duration(self, motion_mode: str) -> int:
        """Suggest duration based on motion mode."""
        duration_map = {
            "static": 4,
            "slow": 6,
            "normal": 6,
            "dynamic": 8,
        }
        return duration_map.get(motion_mode, 6)
