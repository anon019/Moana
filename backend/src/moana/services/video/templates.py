"""Video scene templates for Veo optimization."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SceneTemplate:
    """A predefined scene template with optimized parameters."""
    name: str
    description: str
    duration: int  # 4, 6, or 8 seconds
    motion_mode: str  # static, slow, normal, dynamic
    camera_prompt: str  # Camera movement description for Veo
    negative_prompt: str  # Things to exclude
    resolution: str  # 720p or 1080p


# Predefined scene templates
SCENE_TEMPLATES: dict[str, SceneTemplate] = {
    "cover_subtle": SceneTemplate(
        name="封面微动",
        description="轻微呼吸感，适合封面和标题页",
        duration=4,
        motion_mode="static",
        camera_prompt="static camera, subtle breathing motion, gentle micro-movements",
        negative_prompt="fast movement, camera shake, blur, sudden changes",
        resolution="1080p",
    ),
    "character_dialogue": SceneTemplate(
        name="角色对话",
        description="角色轻微动作和表情变化",
        duration=6,
        motion_mode="slow",
        camera_prompt="medium shot, slight slow zoom in on characters, stable framing",
        negative_prompt="running, jumping, extreme motion, wide shots",
        resolution="720p",
    ),
    "scene_transition": SceneTemplate(
        name="场景转换",
        description="场景推进，带镜头运动",
        duration=8,
        motion_mode="normal",
        camera_prompt="slow cinematic pan across scene, smooth camera movement, establishing shot",
        negative_prompt="static, frozen, no movement, jump cuts",
        resolution="720p",
    ),
    "action_scene": SceneTemplate(
        name="动作场景",
        description="丰富动作，适合高潮情节",
        duration=8,
        motion_mode="dynamic",
        camera_prompt="dynamic tracking shot, follow the action, energetic camera movement",
        negative_prompt="slow, static, frozen expression, boring composition",
        resolution="720p",
    ),
    "emotional_moment": SceneTemplate(
        name="情感特写",
        description="角色表情细腻变化",
        duration=6,
        motion_mode="slow",
        camera_prompt="close-up shot, focus on facial expression, intimate framing, shallow depth of field",
        negative_prompt="wide shot, fast movement, blur, distracting background",
        resolution="1080p",
    ),
}

# Default template for when no template is specified
_DEFAULT_TEMPLATE = SceneTemplate(
    name="默认",
    description="通用默认设置",
    duration=6,
    motion_mode="normal",
    camera_prompt="stable camera, natural movement",
    negative_prompt="blur, distortion, artifacts",
    resolution="720p",
)


def get_template(template_id: str) -> SceneTemplate | None:
    """Get a scene template by ID.

    Args:
        template_id: The template identifier

    Returns:
        SceneTemplate if found, None otherwise
    """
    return SCENE_TEMPLATES.get(template_id)


def get_default_template() -> SceneTemplate:
    """Get the default scene template.

    Returns:
        The default SceneTemplate
    """
    return _DEFAULT_TEMPLATE


def list_templates() -> list[dict]:
    """List all available templates for frontend.

    Returns:
        List of template info dicts
    """
    return [
        {
            "id": template_id,
            "name": template.name,
            "description": template.description,
            "duration": template.duration,
            "resolution": template.resolution,
        }
        for template_id, template in SCENE_TEMPLATES.items()
    ]
