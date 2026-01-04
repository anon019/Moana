# src/moana/api/content.py
import asyncio
import logging
from datetime import datetime
from typing import Annotated, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, desc, literal_column, text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from moana.database import get_db, async_session_factory
from moana.models.content import Content, ContentType, ContentStatus
from moana.pipelines.picture_book import PictureBookPipeline
from moana.pipelines.nursery_rhyme import NurseryRhymePipeline
from moana.pipelines.video import VideoPipeline
from moana.services.music.base import MusicStyle
from moana.themes import get_themes_by_category, Theme

logger = logging.getLogger(__name__)

router = APIRouter()

# ========== 异步任务状态存储 ==========
# 生产环境应使用 Redis
_task_status: dict[str, dict[str, Any]] = {}


# ========== Content List API ==========

class ContentListItem(BaseModel):
    """Single item in content list."""
    id: str
    title: str
    content_type: str
    cover_url: Optional[str] = None
    video_url: Optional[str] = None  # 视频播放地址（仅 video 类型）
    total_duration: Optional[float] = None
    personalization: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    """Response for content list."""
    items: list[ContentListItem]
    total: int
    has_more: bool


@router.get("/list", response_model=ContentListResponse)
async def list_contents(
    db: Annotated[AsyncSession, Depends(get_db)],
    type: Optional[str] = Query(None, description="Filter by content type: picture_book, nursery_rhyme, video"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
):
    """List generated contents with pagination.

    返回用户生成的内容列表，支持按类型过滤和分页。
    """
    # Build query - use literal_column to bypass ORM enum conversion
    ready_status = literal_column("'ready'")
    query = select(Content).where(Content.status == ready_status)

    if type:
        try:
            ContentType(type)  # Validate type
            type_literal = literal_column(f"'{type}'")
            query = query.where(Content.content_type == type_literal)
        except ValueError:
            pass  # Ignore invalid type filter

    # Get total count
    count_query = select(Content).where(Content.status == ready_status)
    if type:
        try:
            ContentType(type)  # Validate type
            type_literal = literal_column(f"'{type}'")
            count_query = count_query.where(Content.content_type == type_literal)
        except ValueError:
            pass

    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get paginated results
    query = query.order_by(desc(Content.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    contents = result.scalars().all()

    # Build response
    items = []
    for content in contents:
        content_data = content.content_data or {}
        content_type = content.content_type.value

        # Extract cover_url and video_url based on content type
        cover_url = None
        video_url = None

        if content_type == "video":
            # 视频类型：video_url + thumbnail_url 作为封面
            video_url = content_data.get("video_url")
            cover_url = content_data.get("thumbnail_url")
        elif content_type == "picture_book":
            # 绘本类型：优先使用缩略图，回退到原图
            pages = content_data.get("pages", [])
            if pages:
                cover_url = pages[0].get("image_thumb_url") or pages[0].get("image_url")
        elif content_type == "nursery_rhyme":
            # 儿歌类型：cover_url 或 suno_cover_url
            cover_url = content_data.get("cover_url") or content_data.get("suno_cover_url")

        items.append(ContentListItem(
            id=content.id,
            title=content.title,
            content_type=content_type,
            cover_url=cover_url,
            video_url=video_url,
            total_duration=content.duration,
            personalization=content.personalization,
            created_at=content.created_at,
        ))

    return ContentListResponse(
        items=items,
        total=total,
        has_more=(offset + len(items)) < total,
    )


# ========== Themes API (must be before /{content_id} to avoid route conflict) ==========

@router.get("/themes")
async def list_themes():
    """List available themes for content generation (enhanced).

    返回增强的主题列表，包含详细元数据。
    """
    def theme_to_dict(t: Theme) -> dict:
        return {
            "id": t.id,
            "name": t.name,
            "subcategory": t.subcategory,
            "age_range": t.age_range,
            "keywords": t.keywords,
        }

    habit_themes = get_themes_by_category("habit")
    cognition_themes = get_themes_by_category("cognition")

    return {
        "habit": {
            "name": "习惯养成",
            "themes": [theme_to_dict(t) for t in habit_themes],
        },
        "cognition": {
            "name": "认知世界",
            "themes": [theme_to_dict(t) for t in cognition_themes],
        },
    }


# ========== Style Options API ==========

@router.get("/style-options")
async def get_style_options():
    """获取所有内容生成的风格选项.

    前端用于展示风格选择界面，适用于绘本、儿歌、视频生成。

    返回：
    - art_styles: 美术风格（用于绘本插图和儿歌封面）
    - protagonists: 主角动物选项
    - color_palettes: 色彩风格
    - accessories: 配饰选项
    - music_moods: 音乐情绪（用于儿歌）
    - video_motion_styles: 视频动效风格
    """
    from moana.styles import get_style_options as get_all_options
    return get_all_options()


# ========== TTS Voices API ==========

# 预览音频 URL 基础路径（存储服务会自动处理路径）
VOICE_PREVIEW_BASE_URL = "https://example.com/media/voice-preview"


@router.get("/tts/voices")
async def get_tts_voices():
    """获取所有可用的 TTS 音色列表.

    前端用于展示音色选择界面，支持试听预览。
    当前仅支持 Gemini TTS，预留扩展其他提供商。

    返回：
    - providers: TTS 提供商列表，每个包含音色数组
    - default_provider: 默认提供商 ID
    - default_voice: 默认音色 ID
    """
    from moana.services.tts.gemini import GeminiTTSService

    # Gemini TTS 音色
    gemini_voices = []
    for voice_id, info in GeminiTTSService.VOICES.items():
        gemini_voices.append({
            "id": voice_id,
            "name": info["name"],
            "name_cn": info["name_cn"],
            "gender": info["gender"],
            "style": info["style"],
            "description": info["description"],
            "recommended": voice_id == GeminiTTSService.DEFAULT_VOICE,
            "preview_url": f"{VOICE_PREVIEW_BASE_URL}/gemini/{voice_id}.wav",
        })

    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "description": "谷歌 Gemini 2.5 Flash TTS，高质量语音合成",
                "voices": gemini_voices,
            }
            # 预留：未来可添加 qwen, minimax 等提供商
        ],
        "default_provider": "gemini",
        "default_voice": GeminiTTSService.DEFAULT_VOICE,
    }


# ========== Video Configuration API ==========

@router.get("/video/config")
async def get_video_config():
    """获取视频生成配置选项.

    前端用于展示视频生成参数选择界面。

    返回：
    - scene_templates: 场景模板列表（预设参数组合）
    - durations: 可选时长（4s, 6s, 8s）
    - resolutions: 可选分辨率（720p, 1080p）
    - negative_prompt_presets: 负面提示词预设
    - enhancement_options: 提示词增强选项
    """
    from moana.services.video.templates import list_templates, SCENE_TEMPLATES
    from moana.services.video.prompt_enhancer import NEGATIVE_PRESETS, STYLE_KEYWORDS

    # Get scene templates
    scene_templates = list_templates()

    # Define duration options
    durations = [
        {"value": 4, "label": "4秒", "description": "快速预览", "providers": ["veo", "wanx"]},
        {"value": 6, "label": "6秒", "description": "标准长度", "recommended": True, "providers": ["veo", "wanx"]},
        {"value": 8, "label": "8秒", "description": "较长动画 (Veo最大)", "providers": ["veo", "wanx"]},
    ]

    # Define resolution options
    resolutions = [
        {"value": "720p", "label": "720P 高清", "pixels": "1280x720", "recommended": True},
        {"value": "1080p", "label": "1080P 全高清", "pixels": "1920x1080"},
    ]

    # Enhancement options
    enhancement_options = {
        "enabled": True,
        "description": "AI自动优化提示词，提升视频质量",
        "styles": list(STYLE_KEYWORDS.keys()),
    }

    return {
        "scene_templates": scene_templates,
        "durations": durations,
        "resolutions": resolutions,
        "negative_prompt_presets": NEGATIVE_PRESETS,
        "enhancement_options": enhancement_options,
    }


# ========== First Frame API ==========

class FirstFrameRequest(BaseModel):
    """Request to generate first frame for video."""
    prompt: str = Field(max_length=500, description="Scene description")
    child_name: str = Field(description="Child's name")
    art_style: str = Field(default="storybook", description="Art style")
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|9:16|1:1)$")


class FirstFrameResponse(BaseModel):
    """Response with generated first frame."""
    image_url: str
    prompt_enhanced: str


class StandaloneVideoRequest(BaseModel):
    """Request for standalone video creation."""
    # Required
    child_name: str = Field(description="Child's name")
    age_months: int = Field(ge=12, le=72, description="Child's age in months")
    custom_prompt: str = Field(max_length=500, description="Video scene description")

    # First frame source (one of these)
    first_frame_url: str | None = Field(default=None, description="Existing first frame URL")
    generate_first_frame: bool = Field(default=True, description="Auto-generate first frame")

    # Video parameters
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|9:16|4:3|3:4|1:1)$")
    resolution: str = Field(default="720P", pattern="^(720P|1080P)$")
    duration_seconds: int = Field(default=5, ge=4, le=8)
    motion_mode: str = Field(default="normal", pattern="^(static|slow|normal|dynamic|cinematic)$")

    # Enhancement options
    art_style: str = Field(default="storybook")
    auto_enhance_prompt: bool = Field(default=True)
    negative_prompt: str | None = Field(default=None)
    scene_template: str | None = Field(default=None)

    @field_validator('first_frame_url', 'generate_first_frame')
    @classmethod
    def validate_first_frame_source(cls, v, info):
        # At least one source must be provided
        return v


@router.post("/video/first-frame", response_model=FirstFrameResponse)
async def generate_first_frame(request: FirstFrameRequest):
    """Generate first frame image for standalone video.

    Synchronous API - returns image_url directly (takes ~5-15 seconds).
    Uses Gemini image generation, saves to local storage.
    """
    from moana.services.image import get_image_service

    logger.info(f"Generating first frame: {request.prompt[:50]}...")

    # Get image service (uses gemini-3-pro-image-preview)
    image_service = get_image_service()

    # Enhance prompt with child name and style
    enhanced_prompt = f"{request.prompt}. 可爱的儿童绘本风格，主角是{request.child_name}最喜欢的小动物角色。"

    try:
        # Calculate dimensions based on aspect ratio
        if request.aspect_ratio == "16:9":
            width, height = 1280, 720
        elif request.aspect_ratio == "9:16":
            width, height = 720, 1280
        else:  # 1:1
            width, height = 1024, 1024

        result = await image_service.generate(
            prompt=enhanced_prompt,
            width=width,
            height=height,
        )

        return FirstFrameResponse(
            image_url=result.url,
            prompt_enhanced=result.revised_prompt or enhanced_prompt,
        )

    except Exception as e:
        logger.error(f"First frame generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "IMAGE_GENERATION_ERROR",
                "message": f"首帧生成失败: {str(e)}",
            }
        )


# ========== Content Detail API ==========

@router.get("/{content_id}")
async def get_content(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get content details by ID.

    返回内容详情，根据内容类型返回扁平化的数据结构：
    - picture_book: 包含 pages 数组、educational_goal、total_interactions
    - nursery_rhyme: 包含 lyrics、audio_url、cover_url、educational_goal
    - video: 包含 video_url、clips、thumbnail_url
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content_data = content.content_data or {}

    # Build base response
    response = {
        "id": content.id,
        "title": content.title,
        "content_type": content.content_type.value,
        "theme_category": content.theme_category,
        "theme_topic": content.theme_topic,
        "personalization": content.personalization,
        "created_at": content.created_at.isoformat() if content.created_at else None,
    }

    # Flatten content_data based on content type
    if content.content_type.value == "picture_book":
        # Picture book specific fields
        # Transform page field names to match frontend expectations:
        # - page_num -> page_number
        # - audio_duration -> duration
        raw_pages = content_data.get("pages", [])
        transformed_pages = []
        for page in raw_pages:
            transformed_page = {
                "page_number": page.get("page_num", page.get("page_number", 0)),
                "text": page.get("text", ""),
                "image_url": page.get("image_url", ""),
                "image_thumb_url": page.get("image_thumb_url"),
                "audio_url": page.get("audio_url", ""),
                "duration": page.get("audio_duration", page.get("duration", 5)),
            }
            # Include interaction if present
            if page.get("interaction"):
                transformed_page["interaction"] = page["interaction"]
            transformed_pages.append(transformed_page)

        response.update({
            "pages": transformed_pages,
            "educational_goal": content_data.get("educational_goal", ""),
            "total_duration": content.duration or sum(p.get("duration", 5) for p in transformed_pages),
            "total_interactions": content_data.get("total_interactions", len([p for p in raw_pages if p.get("interaction")])),
            "cover_url": (raw_pages[0].get("image_thumb_url") or raw_pages[0].get("image_url")) if raw_pages else None,
        })
    elif content.content_type.value == "nursery_rhyme":
        # Nursery rhyme specific fields
        # lyrics 结构: { full_text, timestamped, sections, prompt }
        response.update({
            "lyrics": content_data.get("lyrics", {}),
            "audio_url": content_data.get("audio_url", ""),
            "video_url": content_data.get("video_url", ""),  # Suno 音乐视频
            "audio_duration": content.duration or 0,
            "cover_url": content_data.get("cover_url", ""),  # Imagen 主封面
            "suno_cover_url": content_data.get("suno_cover_url", ""),  # Suno 封面（备用）
            "educational_goal": content_data.get("educational_goal", ""),
            "all_tracks": content_data.get("all_tracks", []),  # 所有歌曲版本
        })
    elif content.content_type.value == "video":
        # Video specific fields
        response.update({
            "video_url": content_data.get("video_url", ""),
            "duration": content.duration or 0,
            "thumbnail_url": content_data.get("thumbnail_url", ""),
            "clips": content_data.get("clips", []),
        })
    else:
        # Fallback: include raw content_data
        response["content_data"] = content_data
        response["duration"] = content.duration

    response["generated_by"] = content.generated_by

    return response


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete content by ID.

    删除指定的内容（绘本、儿歌、视频）。
    注意：相关的媒体文件（图片、音频）不会自动删除，需要定期清理。
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Delete the content
    await db.delete(content)
    await db.commit()

    return {"success": True, "message": "Content deleted successfully"}


@router.get("/{content_id}/generation-logs")
async def get_generation_logs(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取内容的生成日志.

    返回该内容生成过程中的所有日志记录，包括每个步骤的：
    - 输入参数
    - 输出结果
    - 耗时
    - 错误信息（如有）

    用于排查生成失败的原因和分析生成性能。
    """
    # 验证内容存在
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 查询生成日志
    logs_result = await db.execute(
        text("""
            SELECT id, task_id, step, level, sequence, message,
                   input_params, output_result, duration_seconds,
                   error_message, error_traceback, extra_data, created_at
            FROM generation_logs
            WHERE content_id = :content_id
            ORDER BY sequence ASC
        """),
        {"content_id": content_id}
    )
    logs = logs_result.fetchall()

    return {
        "content_id": content_id,
        "logs": [
            {
                "id": log.id,
                "task_id": log.task_id,
                "step": log.step,
                "level": log.level,
                "sequence": log.sequence,
                "message": log.message,
                "input_params": log.input_params,
                "output_result": log.output_result,
                "duration_seconds": log.duration_seconds,
                "error_message": log.error_message,
                "error_traceback": log.error_traceback,
                "extra_data": log.extra_data,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total_count": len(logs),
    }


@router.get("/{content_id}/asset-details")
async def get_asset_details(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取内容的素材详细参数.

    返回优化后的数据结构：
    - generation_config: 通用生成配置（模型、风格等），只记录一次
    - assets: 每个素材只包含独有内容（prompt/text + url）

    这样避免重复存储相同的模型和风格参数。
    """
    # 获取内容
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content_data = content.content_data or {}
    personalization = content.personalization or {}

    # 提取用户输入参数（通用）
    user_inputs = {
        "child_name": personalization.get("child_name", ""),
        "age_months": personalization.get("age_months"),
        "favorite_characters": personalization.get("favorite_characters", []),
        "voice_id": personalization.get("voice_id"),
        "creation_mode": content_data.get("creation_mode", "preset"),
        "custom_prompt": content_data.get("custom_prompt") or content_data.get("user_prompt"),
        "theme_category": content.theme_category,
        "theme_topic": content.theme_topic,
    }

    # 儿歌类型：添加用户选择的所有参数
    if content.content_type.value == "nursery_rhyme":
        user_selections = content_data.get("user_selections", {})
        user_inputs["user_selections"] = user_selections

    # 提取增强参数
    enhancement_params = {
        "story_enhancement": content_data.get("story_enhancement"),
        "visual_enhancement": content_data.get("visual_enhancement"),
    }

    # 儿歌类型：添加提示词增强参数
    if content.content_type.value == "nursery_rhyme":
        enhancement_params["prompt_enhancement"] = {
            "original": content_data.get("user_prompt", ""),
            "enhanced": content_data.get("enhanced_prompt", ""),
            "model": content.generated_by.get("prompt_model", ""),
        }

    # 通用生成配置（只记录一次）
    generation_config = {}
    # 素材列表（每个只包含独有内容）
    assets = []

    # 获取默认模型名称（用于 fallback 旧数据中的 "unknown"）
    from moana.config import get_settings
    settings = get_settings()
    default_image_model = settings.gemini_image_model  # "gemini-3-pro-image-preview"
    default_tts_model = settings.gemini_tts_model  # "gemini-2.5-flash-preview-tts"

    def get_model_name(stored_value: str, default: str) -> str:
        """获取模型名称，如果存储值为 unknown 则使用默认值."""
        return default if stored_value == "unknown" else stored_value

    if content.content_type.value == "picture_book":
        # 从 style_config 获取风格信息
        style_config = content_data.get("style_config", {})
        default_voice_id = personalization.get("voice_id", "Kore")

        # 通用图片配置（只记录一次）
        image_model = content.generated_by.get("image_model", "unknown")
        generation_config["image"] = {
            "model": get_model_name(image_model, default_image_model),
            "style": style_config.get("art_style", "pixar_3d"),
            "width": 1024,
            "height": 1024,
            "protagonist": {
                "animal": style_config.get("protagonist_animal", ""),
                "color": style_config.get("protagonist_color", ""),
                "accessory": style_config.get("protagonist_accessory", ""),
            },
            "color_palette": style_config.get("color_palette", ""),
        }

        # 通用音频配置（只记录一次）
        tts_model = content.generated_by.get("tts_model", "unknown")
        generation_config["audio"] = {
            "model": get_model_name(tts_model, default_tts_model),
            "voice_id": default_voice_id,
        }

        # 绘本：每页有图片和音频，只记录独有内容
        for page in content_data.get("pages", []):
            page_num = page.get("page_num", 0)

            # 图片素材：只记录 prompt（独有内容）
            if page.get("image_url"):
                assets.append({
                    "type": "image",
                    "page_num": page_num,
                    "url": page.get("image_url"),
                    "prompt": page.get("image_prompt", ""),
                })

            # 音频素材：只记录 text 和 duration（独有内容）
            if page.get("audio_url"):
                assets.append({
                    "type": "audio",
                    "page_num": page_num,
                    "url": page.get("audio_url"),
                    "text": page.get("text", ""),
                    "duration": page.get("audio_duration", 0),
                })

    elif content.content_type.value == "nursery_rhyme":
        # 儿歌用户选择参数（30个参数）
        user_selections = content_data.get("user_selections", {})

        # 提示词增强配置
        generation_config["prompt_enhancement"] = {
            "model": content.generated_by.get("prompt_model", "gemini-3-flash-preview"),
            "user_prompt": content_data.get("user_prompt", ""),
            "enhanced_prompt": content_data.get("enhanced_prompt", ""),
        }

        # Suno 音乐生成配置
        generation_config["music"] = {
            "model": content.generated_by.get("music_model", "suno-v5"),
            "generation_mode": content_data.get("generation_mode", "suno_free"),
            # 音乐风格参数
            "music_mood": user_selections.get("music_mood", ""),
            "music_genre": user_selections.get("music_genre", ""),
            "tempo": user_selections.get("tempo", ""),
            "energy_level": user_selections.get("energy_level", ""),
            # 人声参数
            "vocal_type": user_selections.get("vocal_type", ""),
            "vocal_range": user_selections.get("vocal_range", ""),
            "vocal_emotion": user_selections.get("vocal_emotion", ""),
            "vocal_style": user_selections.get("vocal_style", ""),
            "vocal_effects": user_selections.get("vocal_effects", []),
            "vocal_regional": user_selections.get("vocal_regional", ""),
            # 乐器与音效
            "instruments": user_selections.get("instruments", []),
            "sound_effects": user_selections.get("sound_effects", []),
            # 歌词设置
            "lyric_complexity": user_selections.get("lyric_complexity", ""),
            "repetition_level": user_selections.get("repetition_level", ""),
            # 歌曲结构
            "song_structure": user_selections.get("song_structure", ""),
            "duration_preference": user_selections.get("duration_preference", ""),
            "action_types": user_selections.get("action_types", []),
            # 语言文化
            "language": user_selections.get("language", "chinese"),
            "cultural_style": user_selections.get("cultural_style", ""),
            # Suno 进阶控制
            "style_weight": user_selections.get("style_weight", ""),
            "creativity": user_selections.get("creativity", ""),
            "negative_tags": user_selections.get("negative_tags", []),
            "style_description": user_selections.get("style_description", ""),
        }

        # 歌词信息
        lyrics_data = content_data.get("lyrics", {})
        generation_config["lyrics"] = {
            "full_text": lyrics_data.get("full_text", ""),
            "prompt_used": lyrics_data.get("prompt", ""),
            "has_timestamps": bool(lyrics_data.get("timestamped")),
        }

        # 封面图片素材
        if content_data.get("cover_url"):
            assets.append({
                "type": "cover_image",
                "url": content_data.get("cover_url"),
                "source": "suno",  # Suno 自动生成的封面
            })

        # Suno 原始封面（如果不同）
        suno_cover = content_data.get("suno_cover_url")
        if suno_cover and suno_cover != content_data.get("cover_url"):
            assets.append({
                "type": "suno_cover",
                "url": suno_cover,
            })

        # 音频素材
        if content_data.get("audio_url"):
            assets.append({
                "type": "audio",
                "url": content_data.get("audio_url"),
                "duration": content.duration,
                "format": "mp3",
            })

        # 视频素材（如果有）
        if content_data.get("video_url"):
            assets.append({
                "type": "video",
                "url": content_data.get("video_url"),
                "duration": content.duration,
            })

        # 所有音轨（Suno 可能生成多个版本）
        all_tracks = content_data.get("all_tracks", [])
        for i, track in enumerate(all_tracks):
            if i == 0:
                continue  # 跳过主音轨，已经在上面添加
            assets.append({
                "type": "audio_track",
                "track_num": i + 1,
                "url": track.get("audio_url"),
                "duration": track.get("duration"),
                "cover_url": track.get("cover_url"),
            })

    elif content.content_type.value == "video":
        # 通用视频配置
        generation_config["video"] = {
            "model": content.generated_by.get("video_model", "unknown"),
            "resolution": content_data.get("resolution", "720p"),
        }

        # 主视频
        if content_data.get("video_url"):
            assets.append({
                "type": "video",
                "url": content_data.get("video_url"),
                "duration": content.duration,
                "thumbnail_url": content_data.get("thumbnail_url"),
            })

        # 视频片段：只记录 prompt 和 duration
        for i, clip in enumerate(content_data.get("clips", [])):
            assets.append({
                "type": "video_clip",
                "clip_num": i + 1,
                "url": clip.get("video_url"),
                "prompt": clip.get("prompt", ""),
                "duration": clip.get("duration"),
            })

    return {
        "content_id": content_id,
        "content_type": content.content_type.value,
        "generated_by": content.generated_by,
        "user_inputs": user_inputs,
        "enhancement_params": enhancement_params,
        "generation_config": generation_config,
        "assets": assets,
        "total_count": len(assets),
    }


@router.get("/{content_id}/details")
async def get_content_details(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取歌曲详情（用户展示）.

    返回用户友好的歌曲信息，包括：
    - 基本信息（标题、时长、语言、主题）
    - 用户选择的参数
    - 用户输入的提示词（智能模式）
    - 增强后的提示词
    - 生成结果（歌词、音频、封面）
    - 生成模型信息
    """
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content_data = content.content_data or {}
    personalization = content.personalization or {}

    # Basic info
    basic_info = {
        "duration": content.duration or 0,
        "language": content_data.get("style_config", {}).get("language", "普通话"),
        "theme_topic": content.theme_topic,
        "theme_category": content.theme_category,
    }

    # User selections - from content_data.style_config or user_selections column
    user_selections = content.user_selections or content_data.get("style_config", {})
    user_selections["child_name"] = personalization.get("child_name", "")
    user_selections["age_months"] = personalization.get("age_months")
    user_selections["creation_mode"] = content_data.get("creation_mode", "preset")

    # Generation result
    generation_result = {
        "lyrics": content_data.get("lyrics", {}).get("full_text", ""),
        "audio_url": content_data.get("audio_url", ""),
        "cover_url": content_data.get("cover_url", "") or content_data.get("suno_cover_url", ""),
        "video_url": content_data.get("video_url", ""),
        "suno_title": content.title,
        "suno_tags": "",  # Could be extracted from tracks
    }

    return {
        "content_id": content.id,
        "title": content.title,
        "created_at": content.created_at.isoformat() if content.created_at else None,
        "basic_info": basic_info,
        "user_selections": user_selections,
        "user_prompt": content.user_prompt or content_data.get("custom_prompt"),
        "enhanced_prompt": content.enhanced_prompt or content_data.get("lyrics", {}).get("prompt"),
        "generation_result": generation_result,
        "generated_by": content.generated_by or {},
    }


@router.get("/{content_id}/diagnostics")
async def get_content_diagnostics(
    content_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取内容诊断信息（故障排查）.

    返回完整的生成链路信息，包括：
    - 时间线（各阶段时间戳）
    - 各阶段耗时
    - 原始请求参数
    - 提示词增强详情
    - Suno 调用详情
    - 所有生成的歌曲
    - 错误和警告信息
    """
    # Get content
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content_data = content.content_data or {}
    personalization = content.personalization or {}

    # Get generation logs
    logs_result = await db.execute(
        text("""
            SELECT step, message, input_params, output_result,
                   duration_seconds, error_message, created_at
            FROM generation_logs
            WHERE content_id = :content_id
            ORDER BY sequence ASC
        """),
        {"content_id": content_id}
    )
    logs = logs_result.fetchall()

    # Build timeline from logs
    timeline = {
        "created_at": content.created_at.isoformat() if content.created_at else None,
    }
    stage_durations = {}
    prompt_enhancement = {}
    suno_details = {}
    errors = []

    for log in logs:
        step = log.step
        if log.error_message:
            errors.append({
                "step": step,
                "message": log.error_message,
            })

        if log.duration_seconds:
            stage_durations[step] = log.duration_seconds

        if step == "prompt_enhance":
            prompt_enhancement = {
                "input_template": log.input_params.get("template", "") if log.input_params else "",
                "final_prompt": log.output_result.get("enhanced", "") if log.output_result else "",
                "prompt_length": log.output_result.get("length", 0) if log.output_result else 0,
            }
            timeline["prompt_enhanced_at"] = log.created_at.isoformat() if log.created_at else None

        if step == "music_generate":
            suno_details = {
                "request": {"prompt": log.input_params.get("prompt", "")[:200] if log.input_params else ""},
                "response": log.output_result if log.output_result else {},
            }
            timeline["suno_completed_at"] = log.created_at.isoformat() if log.created_at else None

    # Calculate total duration
    if stage_durations:
        timeline["total_duration_seconds"] = sum(stage_durations.values())

    # Build raw request from personalization and content_data
    raw_request = {
        "child_name": personalization.get("child_name"),
        "age_months": personalization.get("age_months"),
        "creation_mode": content_data.get("creation_mode", "preset"),
        "theme_topic": content.theme_topic,
        "theme_category": content.theme_category,
        **content_data.get("style_config", {}),
    }

    # All tracks
    all_tracks = content_data.get("all_tracks", [])
    formatted_tracks = []
    for i, track in enumerate(all_tracks):
        formatted_tracks.append({
            "track_id": track.get("id", f"track_{i+1}"),
            "title": track.get("title", ""),
            "duration": track.get("duration", 0),
            "is_primary": i == 0,
            "audio_url": track.get("audio_url", ""),
            "cover_url": track.get("cover_url", ""),
            "lyrics": track.get("lyric", "")[:200] + "..." if len(track.get("lyric", "")) > 200 else track.get("lyric", ""),
        })

    return {
        "content_id": content.id,
        "task_id": content_data.get("task_id"),
        "status": content.status.value if hasattr(content.status, 'value') else str(content.status),
        "timeline": timeline,
        "stage_durations": stage_durations,
        "raw_request": raw_request,
        "prompt_enhancement": prompt_enhancement,
        "suno_details": suno_details,
        "all_tracks": formatted_tracks,
        "errors": errors,
        "warnings": [],
    }


# ========== Helper function to save content ==========

async def save_content_to_db(
    db: AsyncSession,
    title: str,
    content_type: ContentType,
    theme_category: str,
    theme_topic: str,
    personalization: dict,
    content_data: dict,
    duration: Optional[int],
    generated_by: dict,
    child_id: Optional[str] = None,
) -> str:
    """Save generated content to database using raw SQL to avoid enum issues."""
    import json

    content_id = str(uuid4())

    # Use raw SQL to insert with proper enum values
    sql = text("""
        INSERT INTO contents (
            id, child_id, title, content_type, theme_category, theme_topic,
            personalization, content_data, status, review_status, review_result,
            generated_by, duration
        ) VALUES (
            :id, :child_id, :title, :content_type, :theme_category, :theme_topic,
            :personalization, :content_data, 'ready', 'pending', '{}',
            :generated_by, :duration
        )
    """)

    await db.execute(sql, {
        "id": content_id,
        "child_id": child_id,
        "title": title,
        "content_type": content_type.value,  # 'picture_book'
        "theme_category": theme_category,  # 'habit'
        "theme_topic": theme_topic,
        "personalization": json.dumps(personalization),
        "content_data": json.dumps(content_data),
        "generated_by": json.dumps(generated_by),
        "duration": duration,
    })
    await db.commit()

    return content_id


class ProtagonistConfig(BaseModel):
    """主角配置."""
    animal: str | None = Field(default="bunny", description="动物类型: bunny, bear, cat, dog, panda, fox")
    color: str | None = Field(default="white", description="主色: white, brown, orange, golden 等")
    accessory: str | None = Field(default=None, description="配饰: blue overalls, red scarf 等")

    @field_validator('animal', 'color', mode='before')
    @classmethod
    def convert_null_to_default(cls, v, info):
        """Convert null to None, letting Field default take over."""
        if v is None:
            # Return the field's default value
            defaults = {'animal': 'bunny', 'color': 'white'}
            return defaults.get(info.field_name)
        return v


class StoryEnhancementConfig(BaseModel):
    """故事增强配置（全部可选，由 Gemini 智能推断）."""
    narrative_pace: str | None = Field(default=None, description="叙事节奏: relaxed(舒缓)/lively(活泼)/progressive(渐进)")
    interaction_density: str | None = Field(default=None, description="互动密度: minimal(少)/moderate(适中)/intensive(多)")
    educational_focus: str | None = Field(default=None, description="教育侧重: cognitive/behavioral/emotional/imaginative")
    language_style: str | None = Field(default=None, description="语言风格: simple/rhythmic/onomatopoeia/repetitive")
    plot_complexity: str | None = Field(default=None, description="情节复杂度: linear/twist/ensemble")
    ending_style: str | None = Field(default=None, description="结局风格: warm/open/summary")


class VisualEnhancementConfig(BaseModel):
    """视觉增强配置（全部可选，由 Gemini 智能推断）."""
    time_atmosphere: str | None = Field(default=None, description="时间氛围: morning/afternoon/sunset/night/dreamy")
    scene_environment: str | None = Field(default=None, description="场景环境: indoor/garden/forest/beach/clouds")
    emotional_tone: str | None = Field(default=None, description="情感基调: cheerful/cozy/playful/peaceful/curious")
    composition_style: str | None = Field(default=None, description="画面构图: close_up/panorama/interaction/narrative")
    lighting_effect: str | None = Field(default=None, description="光照效果: soft_natural/warm_sunlight/dreamy_glow/cozy_lamp")


class PictureBookRequest(BaseModel):
    """Request to generate a picture book."""
    child_name: str = Field(description="Child's name to personalize the story")
    age_months: int = Field(ge=12, le=72, description="Child's age in months")

    # Smart mode: these become optional
    theme_topic: str = Field(default="", description="Theme/topic (optional in smart mode)")
    theme_category: str = Field(default="", description="Category (optional in smart mode)")

    favorite_characters: list[str] | None = Field(
        default=None,
        description="Child's favorite characters to include"
    )
    voice_id: str | None = Field(
        default=None,
        description="Voice ID for TTS (e.g., cloned mother's voice)"
    )
    # ===== 新增风格参数 =====
    art_style: str | None = Field(
        default="pixar_3d",
        description="美术风格: pixar_3d, watercolor, flat_vector, crayon, anime"
    )
    protagonist: ProtagonistConfig | None = Field(
        default=None,
        description="主角设定"
    )
    color_palette: str | None = Field(
        default="pastel",
        description="色彩风格: pastel, vibrant, warm, cool, monochrome"
    )

    # NEW: Smart creation fields
    creation_mode: str = Field(
        default="preset",
        pattern="^(smart|preset)$",
        description="Creation mode: smart or preset"
    )
    custom_prompt: str | None = Field(
        default=None,
        max_length=500,
        description="Custom description for smart mode"
    )
    # === 新增：增强配置 ===
    story_enhancement: StoryEnhancementConfig | None = Field(
        default=None,
        description="故事创作增强参数（可选）"
    )
    visual_enhancement: VisualEnhancementConfig | None = Field(
        default=None,
        description="视觉风格增强参数（可选）"
    )


class PictureBookResponse(BaseModel):
    """Response containing generated picture book."""
    title: str
    theme_topic: str
    educational_goal: str
    pages: list[dict]
    total_duration: float
    total_interactions: int
    personalization: dict
    generated_by: dict


class AsyncTaskResponse(BaseModel):
    """Response for async task creation."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for task status query."""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    stage: str | None = None  # 阶段代码: pending, story, image_1, image_2, audio, completed
    message: str | None = None  # 人类可读消息: "正在生成第1张插图..."
    content_id: str | None = None  # 完成后的内容ID
    result: dict | None = None  # 完成后的结果
    error: str | None = None


async def _generate_picture_book_background(
    task_id: str,
    child_name: str,
    age_months: int,
    theme_topic: str,
    theme_category: str,
    favorite_characters: list[str] | None,
    voice_id: str | None,
    # ===== 新增风格参数 =====
    art_style: str | None = None,
    protagonist_animal: str | None = None,
    protagonist_color: str | None = None,
    protagonist_accessory: str | None = None,
    color_palette: str | None = None,
    # ===== 新增增强参数 =====
    story_enhancement: dict | None = None,
    visual_enhancement: dict | None = None,
    # ===== 用户输入参数 =====
    creation_mode: str = "preset",
    custom_prompt: str | None = None,
):
    """后台执行绘本生成任务."""
    try:
        _task_status[task_id] = {
            "status": "processing",
            "progress": 5,
            "stage": "init",
            "message": "初始化...",
        }

        pipeline = PictureBookPipeline()

        _task_status[task_id].update({
            "progress": 10,
            "stage": "story",
            "message": "正在创作故事...",
        })

        def on_progress(progress):
            """进度回调 - 接收 GenerationProgress 对象.

            进度分配 (总计 100%):
            - init: 0-5%
            - story: 5-20%
            - images: 20-70% (按图片数量均分)
            - audio: 70-95% (按音频数量均分)
            - save: 95-100%
            """
            # 阶段代码映射
            stage_code = progress.stage  # outline, images, audio
            current = progress.current
            total = progress.total

            if stage_code == "outline":
                # 故事生成完成
                stage = "story_done" if current >= total else "story"
                base_progress = 10
                stage_range = 10  # 10-20%
                calculated_progress = base_progress + int(stage_range * current / max(total, 1))

            elif stage_code == "images":
                # 图片生成: 20-70%，每张图片均分
                stage = f"image_{current}" if current > 0 else "image_1"
                base_progress = 20
                stage_range = 50  # 20-70%
                calculated_progress = base_progress + int(stage_range * current / max(total, 1))

            elif stage_code == "audio":
                # 音频生成: 70-95%，每个音频均分
                stage = f"audio_{current}" if current > 0 else "audio_1"
                base_progress = 70
                stage_range = 25  # 70-95%
                calculated_progress = base_progress + int(stage_range * current / max(total, 1))

            else:
                stage = stage_code
                calculated_progress = 50

            _task_status[task_id].update({
                "progress": calculated_progress,
                "stage": stage,
                "message": progress.message,
            })

        result = await pipeline.generate(
            child_name=child_name,
            age_months=age_months,
            theme_topic=theme_topic,
            theme_category=theme_category,
            favorite_characters=favorite_characters,
            voice_id=voice_id,
            on_progress=on_progress,
            # 传递风格参数
            art_style=art_style,
            protagonist_animal=protagonist_animal,
            protagonist_color=protagonist_color,
            protagonist_accessory=protagonist_accessory,
            color_palette=color_palette,
            # 传递增强参数
            story_enhancement=story_enhancement,
            visual_enhancement=visual_enhancement,
            # 传递任务 ID 用于日志记录
            task_id=task_id,
        )

        _task_status[task_id].update({
            "progress": 95,
            "stage": "saving",
            "message": "保存到数据库...",
        })

        # 使用独立的数据库会话保存
        async with async_session_factory() as db:
            # 合并 personalization 和用户输入参数
            personalization = result.get("personalization", {})
            personalization["age_months"] = age_months
            if voice_id:
                personalization["voice_id"] = voice_id

            content_id = await save_content_to_db(
                db=db,
                title=result["title"],
                content_type=ContentType.PICTURE_BOOK,
                theme_category=theme_category,
                theme_topic=theme_topic,
                personalization=personalization,
                content_data={
                    "pages": result.get("pages", []),
                    "educational_goal": result.get("educational_goal", ""),
                    "total_interactions": result.get("total_interactions", 0),
                    # 保存风格配置
                    "style_config": result.get("style_config", {}),
                    # 保存用户输入的增强参数
                    "story_enhancement": story_enhancement,
                    "visual_enhancement": visual_enhancement,
                    # 保存创作模式和自定义提示词
                    "creation_mode": creation_mode,
                    "custom_prompt": custom_prompt,
                },
                duration=int(result.get("total_duration", 0)),
                generated_by=result.get("generated_by", {}),
            )

            # 更新生成日志的 content_id
            from moana.services.logging import GenerationLogger
            gen_logger = GenerationLogger(task_id=task_id)
            await gen_logger.update_content_id(content_id)

        _task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "stage": "completed",
            "message": "生成完成",
            "content_id": content_id,
            "result": result,
        }
        logger.info(f"Picture book task {task_id} completed, content_id={content_id}")

    except Exception as e:
        logger.exception(f"Picture book task {task_id} failed: {e}")
        _task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "stage": "failed",
            "message": "生成失败",
            "error": str(e),
        }


@router.post("/picture-book/async", response_model=AsyncTaskResponse)
async def generate_picture_book_async(
    request: PictureBookRequest,
):
    """异步生成绘本，立即返回 task_id，前端轮询状态.

    这是推荐的调用方式，避免 Cloudflare 超时。
    绘本生成通常需要 2-3 分钟，超过 Cloudflare 100 秒限制。

    支持自定义风格参数：
    - art_style: 美术风格 (pixar_3d, watercolor, flat_vector, crayon, anime)
    - protagonist: 主角设定 (animal, color, accessory)
    - color_palette: 色彩风格 (pastel, vibrant, warm, cool, monochrome)

    支持两种创作模式：
    - preset: 预设主题模式，需要提供 theme_topic 和 theme_category
    - smart: 智能创作模式，需要提供 custom_prompt，AI 自动推断主题
    """
    # 记录风格参数用于调试
    logger.info(f"[PictureBook] Request received - art_style={request.art_style}, "
                f"protagonist={request.protagonist}, "
                f"color_palette={request.color_palette}, "
                f"child_name={request.child_name}")

    task_id = str(uuid4())

    # 初始化任务状态
    _task_status[task_id] = {
        "status": "pending",
        "progress": 0,
        "stage": "pending",
        "message": "排队中...",
    }

    # Handle smart mode
    theme_topic = request.theme_topic
    theme_category = request.theme_category

    if request.creation_mode == "smart":
        from moana.services.smart import SmartPromptAnalyzer

        if not request.custom_prompt:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "message": "智能创作模式下必须提供 custom_prompt"}
            )

        logger.info(f"Smart mode: analyzing prompt '{request.custom_prompt[:50]}...'")

        analyzer = SmartPromptAnalyzer()
        analysis = await analyzer.analyze(
            custom_prompt=request.custom_prompt,
            child_name=request.child_name,
            age_months=request.age_months,
            content_type="picture_book",
        )
        theme_topic = analysis.theme_topic
        theme_category = analysis.theme_category

        logger.info(f"Smart mode: inferred topic='{theme_topic}', category='{theme_category}'")
    else:  # preset mode
        # Validate that theme_topic and theme_category are provided
        if not theme_topic or not theme_category:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "message": "预设模式下必须提供 theme_topic 和 theme_category"}
            )

    # 解析主角设定
    protagonist = request.protagonist
    protagonist_animal = protagonist.animal if protagonist else None
    protagonist_color = protagonist.color if protagonist else None
    protagonist_accessory = protagonist.accessory if protagonist else None

    # 使用 asyncio.create_task 立即开始执行
    asyncio.create_task(
        _generate_picture_book_background(
            task_id=task_id,
            child_name=request.child_name,
            age_months=request.age_months,
            theme_topic=theme_topic,
            theme_category=theme_category,
            favorite_characters=request.favorite_characters,
            voice_id=request.voice_id,
            # 传递风格参数
            art_style=request.art_style,
            protagonist_animal=protagonist_animal,
            protagonist_color=protagonist_color,
            protagonist_accessory=protagonist_accessory,
            color_palette=request.color_palette,
            # 传递增强参数
            story_enhancement=request.story_enhancement.model_dump() if request.story_enhancement else None,
            visual_enhancement=request.visual_enhancement.model_dump() if request.visual_enhancement else None,
            # 传递用户输入参数
            creation_mode=request.creation_mode,
            custom_prompt=request.custom_prompt,
        )
    )

    return AsyncTaskResponse(
        task_id=task_id,
        status="pending",
        message="绘本生成任务已创建，请轮询状态",
    )


@router.get("/picture-book/status/{task_id}", response_model=TaskStatusResponse)
async def get_picture_book_status(task_id: str):
    """查询绘本生成任务状态.

    前端应每 3-5 秒轮询一次，直到 status 为 completed 或 failed。
    """
    if task_id not in _task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    status = _task_status[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=status.get("status", "unknown"),
        progress=status.get("progress", 0),
        stage=status.get("stage"),
        message=status.get("message"),
        content_id=status.get("content_id"),
        result=status.get("result"),
        error=status.get("error"),
    )


@router.post("/picture-book", response_model=PictureBookResponse)
async def generate_picture_book(
    request: PictureBookRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """同步生成绘本（可能超时，建议使用 /picture-book/async）."""
    pipeline = PictureBookPipeline()

    # 解析主角设定
    protagonist = request.protagonist
    protagonist_animal = protagonist.animal if protagonist else None
    protagonist_color = protagonist.color if protagonist else None
    protagonist_accessory = protagonist.accessory if protagonist else None

    try:
        result = await pipeline.generate(
            child_name=request.child_name,
            age_months=request.age_months,
            theme_topic=request.theme_topic,
            theme_category=request.theme_category,
            favorite_characters=request.favorite_characters,
            voice_id=request.voice_id,
            # 传递风格参数
            art_style=request.art_style,
            protagonist_animal=protagonist_animal,
            protagonist_color=protagonist_color,
            protagonist_accessory=protagonist_accessory,
            color_palette=request.color_palette,
        )

        # Save to database
        await save_content_to_db(
            db=db,
            title=result["title"],
            content_type=ContentType.PICTURE_BOOK,
            theme_category=request.theme_category,
            theme_topic=request.theme_topic,
            personalization=result.get("personalization", {}),
            content_data={
                "pages": result.get("pages", []),
                "educational_goal": result.get("educational_goal", ""),
                "total_interactions": result.get("total_interactions", 0),
            },
            duration=int(result.get("total_duration", 0)),
            generated_by=result.get("generated_by", {}),
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NurseryRhymeRequest(BaseModel):
    """Request to generate a nursery rhyme (V2 with 31+ parameters).

    采用宽松验证策略：
    - 仅校验必填参数（child_name, age_months）
    - 其他所有参数透传给 PromptEnhancer，由 Gemini 处理
    - 支持前端任意新增参数，无需修改后端
    """
    # === 基础参数（可选，有默认值）===
    child_name: str | None = Field(default="宝宝", description="Child's name to personalize the song")
    age_months: int | None = Field(default=36, ge=12, le=72, description="Child's age in months")

    # === 主题参数 ===
    theme_topic: str | None = Field(default="", description="Theme/topic of the song")
    theme_category: str | None = Field(default="", description="Category: habit or cognition")

    # === 创作模式 ===
    creation_mode: str | None = Field(default="preset", description="preset or smart")
    custom_prompt: str | None = Field(default=None, max_length=500, description="Smart mode description")

    @field_validator('child_name', mode='before')
    @classmethod
    def validate_child_name(cls, v):
        """Ensure child_name is a valid string."""
        if v is None or v == "":
            return "宝宝"  # Default name
        return str(v)

    @field_validator('age_months', mode='before')
    @classmethod
    def validate_age_months(cls, v):
        """Ensure age_months is a valid integer."""
        if v is None:
            return 36  # Default age
        try:
            return int(v)
        except (ValueError, TypeError):
            return 36

    @field_validator('theme_topic', 'theme_category', 'creation_mode', mode='before')
    @classmethod
    def convert_null_to_empty(cls, v, info):
        """Convert null to default value."""
        if v is None:
            defaults = {'theme_topic': '', 'theme_category': '', 'creation_mode': 'preset'}
            return defaults.get(info.field_name, '')
        return v

    # === 音乐风格（透传，不校验枚举）===
    music_mood: str | None = Field(default=None, description="Music mood/emotion")
    music_genre: str | None = Field(default=None, description="Music genre")
    tempo: int | str | None = Field(default=None, description="Tempo BPM (60-180)")
    energy_level: int | str | None = Field(default=None, description="Energy level (1-10)")

    # === 人声设置（透传）===
    vocal_type: str | None = Field(default=None, description="Vocal type")
    vocal_range: str | None = Field(default=None, description="Vocal range: high/mid/low")
    vocal_emotion: str | None = Field(default=None, description="Vocal emotion")
    vocal_style: str | None = Field(default=None, description="Vocal style")
    vocal_effects: list[str] | None = Field(default=None, description="Vocal effects")
    vocal_regional: str | None = Field(default=None, description="Regional vocal style")

    # === 乐器与音效（透传）===
    instruments: list[str] | None = Field(default=None, description="Instruments list")
    sound_effects: list[str] | None = Field(default=None, description="Sound effects list")

    # === 歌词设置（透传）===
    lyric_complexity: int | str | None = Field(default=None, description="Lyric complexity (1-10)")
    repetition_level: int | str | None = Field(default=None, description="Repetition level (1-10)")

    # === 歌曲结构（透传）===
    song_structure: str | None = Field(default=None, description="Song structure type")
    duration_preference: int | str | None = Field(default=None, description="Preferred duration in seconds")
    action_types: str | None = Field(default=None, description="Action types for interaction")

    # === 语言文化（透传）===
    language: str | None = Field(default=None, description="Song language")
    cultural_style: str | None = Field(default=None, description="Cultural style")

    # === 个性化（透传）===
    educational_focus: str | list[str] | None = Field(default=None, description="Educational focus")
    favorite_characters: list[str] | None = Field(default=None, description="Favorite characters")
    favorite_colors: list[str] | None = Field(default=None, description="Favorite colors")

    # === Suno 进阶控制 ===
    style_weight: float | None = Field(default=0.5, ge=0, le=1, description="Style weight (0-1)")
    creativity: float | None = Field(default=0.5, ge=0, le=1, description="Creativity level (0-1)")
    negative_tags: str | None = Field(default=None, description="Tags to exclude")
    style_description: str | None = Field(default=None, description="Custom style description")
    seed: int | None = Field(default=None, description="Random seed for reproducibility")

    # === 兼容旧参数 ===
    music_style: str | None = Field(default="cheerful", description="Legacy music style")
    art_style: str | None = Field(default=None, description="Cover art style")
    protagonist: ProtagonistConfig | None = Field(default=None, description="Cover protagonist")
    color_palette: str | None = Field(default=None, description="Color palette")

    @field_validator('style_weight', 'creativity', mode='before')
    @classmethod
    def convert_null_to_float_default(cls, v, info):
        """Convert null to default float value."""
        if v is None:
            return 0.5
        return v

    @field_validator('music_style', mode='before')
    @classmethod
    def convert_null_music_style(cls, v):
        """Convert null to default music style."""
        if v is None or v == "":
            return "cheerful"
        return v

    # 允许额外字段透传
    model_config = {"extra": "allow"}

    def to_enhancer_params(self) -> dict:
        """Convert all parameters to dict for PromptEnhancer.

        Returns all non-None parameters for prompt enhancement.
        child_name 保留用于标题生成，但不会传递给 Suno 提示词（由 PromptEnhancer 控制）。
        """
        # 获取所有字段值
        data = self.model_dump(exclude_none=True)

        # child_name 保留，用于标题和个性化信息

        # 处理 protagonist 嵌套对象
        if self.protagonist:
            data["protagonist_animal"] = self.protagonist.animal
            data["protagonist_color"] = self.protagonist.color
            data["protagonist_accessory"] = self.protagonist.accessory
            del data["protagonist"]

        # 兼容 vocal_type -> vocal_gender
        if "vocal_type" in data and "vocal_gender" not in data:
            data["vocal_gender"] = data["vocal_type"]

        # 兼容 action_types -> has_actions
        if "action_types" in data:
            data["has_actions"] = True

        return data


class NurseryRhymeResponse(BaseModel):
    """Response containing generated nursery rhyme."""
    title: str
    theme_topic: str
    educational_goal: str
    lyrics: dict
    audio_url: str
    audio_duration: float
    cover_url: str
    personalization: dict
    generated_by: dict


async def _generate_nursery_rhyme_background(
    task_id: str,
    params: dict,
):
    """后台执行儿歌生成任务（V2 redesign - 参数透传）.

    Args:
        task_id: 任务ID
        params: 所有请求参数的字典，直接透传给 Pipeline
    """
    # 提取必需参数
    child_name = params.get("child_name", "宝宝")
    age_months = params.get("age_months", 36)
    theme_topic = params.get("theme_topic", "")
    theme_category = params.get("theme_category", "habit")
    creation_mode = params.get("creation_mode", "preset")
    custom_prompt = params.get("custom_prompt")
    music_style_str = params.get("music_style", "cheerful")

    # 转换 music_style 枚举
    style_map = {
        "cheerful": MusicStyle.CHEERFUL,
        "gentle": MusicStyle.GENTLE,
        "playful": MusicStyle.PLAYFUL,
        "lullaby": MusicStyle.LULLABY,
        "educational": MusicStyle.EDUCATIONAL,
    }
    music_style = style_map.get(music_style_str, MusicStyle.CHEERFUL)

    try:
        _task_status[task_id] = {
            "status": "processing",
            "progress": 5,
            "stage": "init",
            "message": "初始化...",
        }

        pipeline = NurseryRhymePipeline()

        def on_progress(progress):
            """进度回调 - 儿歌进度分配:
            - init: 0-10%
            - lyrics: 10-30%
            - music: 30-80%
            - cover: 80-95%
            """
            stage_code = progress.stage
            current = progress.current
            total = progress.total

            if stage_code == "lyrics":
                stage = "lyrics"
                calculated_progress = 20
            elif stage_code == "music":
                stage = "music"
                base_progress = 30
                stage_range = 50
                calculated_progress = base_progress + int(stage_range * current / max(total, 1))
            elif stage_code == "cover":
                stage = "cover"
                calculated_progress = 85
            else:
                stage = stage_code
                calculated_progress = 50

            _task_status[task_id].update({
                "progress": calculated_progress,
                "stage": stage,
                "message": progress.message,
            })

        _task_status[task_id].update({
            "progress": 10,
            "stage": "lyrics",
            "message": "正在创作歌词...",
        })

        # V2: 直接传递 params dict 给 pipeline
        result = await pipeline.generate_v2(
            params=params,
            music_style=music_style,
            on_progress=on_progress,
            task_id=task_id,
        )

        _task_status[task_id].update({
            "progress": 95,
            "stage": "saving",
            "message": "保存到数据库...",
        })

        # 使用独立的数据库会话保存
        async with async_session_factory() as db:
            # 合并 personalization 和用户输入参数
            personalization = result.get("personalization", {})
            personalization["age_months"] = age_months

            content_id = await save_content_to_db(
                db=db,
                title=result["title"],
                content_type=ContentType.NURSERY_RHYME,
                theme_category=theme_category,
                theme_topic=theme_topic,
                personalization=personalization,
                content_data={
                    "lyrics": result.get("lyrics", {}),
                    "audio_url": result.get("audio_url", ""),
                    "video_url": result.get("video_url", ""),
                    "cover_url": result.get("cover_url", ""),
                    "suno_cover_url": result.get("suno_cover_url", ""),
                    "educational_goal": result.get("educational_goal", ""),
                    "all_tracks": result.get("all_tracks", []),
                    "generation_mode": result.get("generation_mode", ""),
                    "task_id": result.get("task_id", ""),
                    # 保存创作模式和自定义提示词
                    "creation_mode": creation_mode,
                    "custom_prompt": custom_prompt,
                    # 保存用户选择的所有参数
                    "style_config": result.get("user_selections", params),
                },
                duration=int(result.get("audio_duration", 0)),
                generated_by=result.get("generated_by", {}),
            )

            # Update generation logs with content_id
            from moana.services.logging import GenerationLogger
            gen_logger = GenerationLogger(task_id=task_id)
            await gen_logger.update_content_id(content_id)

        _task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "stage": "completed",
            "message": "生成完成",
            "content_id": content_id,
            "result": result,
        }
        logger.info(f"Nursery rhyme task {task_id} completed, content_id={content_id}")

    except Exception as e:
        logger.exception(f"Nursery rhyme task {task_id} failed: {e}")
        _task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "stage": "failed",
            "message": "生成失败",
            "error": str(e),
        }


@router.post("/nursery-rhyme/async", response_model=AsyncTaskResponse)
async def generate_nursery_rhyme_async(
    request: NurseryRhymeRequest,
    background_tasks: BackgroundTasks,
):
    """异步生成儿歌，立即返回 task_id，前端轮询状态.

    V2 redesign: 支持 31+ 参数透传，所有参数直接传给 PromptEnhancer。

    支持两种创作模式：
    - preset: 预设主题模式，需要提供 theme_topic 和 theme_category
    - smart: 智能创作模式，需要提供 custom_prompt，AI 自动推断主题

    参数说明见 nursery-rhyme-v2-api-guide.md
    """
    task_id = str(uuid4())

    # 初始化任务状态
    _task_status[task_id] = {
        "status": "pending",
        "progress": 0,
        "stage": "pending",
        "message": "排队中...",
    }

    # 获取所有参数（透传给 PromptEnhancer）
    params = request.to_enhancer_params()

    # Handle smart mode
    theme_topic = params.get("theme_topic", "")
    theme_category = params.get("theme_category", "")

    if request.creation_mode == "smart":
        from moana.services.smart import SmartPromptAnalyzer

        if not request.custom_prompt:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "message": "智能创作模式下必须提供 custom_prompt"}
            )

        logger.info(f"Smart mode: analyzing prompt '{request.custom_prompt[:50]}...'")

        analyzer = SmartPromptAnalyzer()
        analysis = await analyzer.analyze(
            custom_prompt=request.custom_prompt,
            child_name=request.child_name,
            age_months=request.age_months,
            content_type="nursery_rhyme",
        )
        theme_topic = analysis.theme_topic
        theme_category = analysis.theme_category

        # 更新 params 中的主题信息
        params["theme_topic"] = theme_topic
        params["theme_category"] = theme_category

        logger.info(f"Smart mode: inferred topic='{theme_topic}', category='{theme_category}'")
    else:  # preset mode
        # Validate that theme_topic and theme_category are provided
        if not theme_topic or not theme_category:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "message": "预设模式下必须提供 theme_topic 和 theme_category"}
            )

    logger.info(f"[NurseryRhyme V2] Received {len(params)} parameters for task {task_id}")

    # 使用 asyncio.create_task 立即开始执行
    asyncio.create_task(
        _generate_nursery_rhyme_background(
            task_id=task_id,
            params=params,
        )
    )

    return AsyncTaskResponse(
        task_id=task_id,
        status="pending",
        message="儿歌生成任务已创建，请轮询状态",
    )


@router.get("/nursery-rhyme/status/{task_id}")
async def get_nursery_rhyme_status(task_id: str, response: Response):
    """查询儿歌生成任务状态.

    前端应每 3-5 秒轮询一次，直到 status 为 completed 或 failed。
    """
    # 防止 CDN 缓存状态响应
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    if task_id not in _task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    status = _task_status[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=status.get("status", "unknown"),
        progress=status.get("progress", 0),
        stage=status.get("stage"),
        message=status.get("message"),
        content_id=status.get("content_id"),
        result=status.get("result"),
        error=status.get("error"),
    )


@router.post("/nursery-rhyme", response_model=NurseryRhymeResponse)
async def generate_nursery_rhyme(
    request: NurseryRhymeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """同步生成儿歌（可能超时，建议使用 /nursery-rhyme/async）."""
    pipeline = NurseryRhymePipeline()

    style_map = {
        "cheerful": MusicStyle.CHEERFUL,
        "gentle": MusicStyle.GENTLE,
        "playful": MusicStyle.PLAYFUL,
        "lullaby": MusicStyle.LULLABY,
        "educational": MusicStyle.EDUCATIONAL,
    }
    music_style = style_map.get(request.music_mood or "cheerful", MusicStyle.CHEERFUL)

    # Build params dict from request
    params = request.model_dump(exclude_none=True)

    try:
        result = await pipeline.generate(
            params=params,
            music_style=music_style,
        )

        # Save to database
        await save_content_to_db(
            db=db,
            title=result["title"],
            content_type=ContentType.NURSERY_RHYME,
            theme_category=request.theme_category,
            theme_topic=request.theme_topic,
            personalization=result.get("personalization", {}),
            content_data={
                "lyrics": result.get("lyrics", {}),
                "audio_url": result.get("audio_url", ""),
                "video_url": result.get("video_url", ""),
                "cover_url": result.get("cover_url", ""),
                "suno_cover_url": result.get("suno_cover_url", ""),
                "educational_goal": result.get("educational_goal", ""),
                "all_tracks": result.get("all_tracks", []),
                "generation_mode": result.get("generation_mode", ""),
                "task_id": result.get("task_id", ""),
            },
            duration=int(result.get("audio_duration", 0)),
            generated_by=result.get("generated_by", {}),
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class VideoRequest(BaseModel):
    """Request to generate video from picture book."""
    picture_book: dict = Field(
        description="Picture book data with title and pages"
    )
    child_name: str = Field(default="", description="Child's name for personalization")
    theme_topic: str = Field(default="", description="Theme topic")
    theme_category: str = Field(default="cognition", description="Theme category")
    # ===== 新增风格参数 =====
    motion_style: str | None = Field(
        default="gentle",
        description="视频动效风格: gentle(轻柔缓动), dynamic(活泼动感), static(静态展示)"
    )


class VideoResponse(BaseModel):
    """Response containing generated video."""
    id: Optional[str] = None
    title: str
    video_url: str
    duration: float
    thumbnail_url: str
    clips: list[dict]
    generated_by: dict


async def _generate_video_background(
    task_id: str,
    picture_book_data: dict,
    child_name: str,
    theme_topic: str,
    theme_category: str,
    motion_style: str | None = None,
):
    """后台执行视频生成任务."""
    try:
        _task_status[task_id] = {
            "status": "processing",
            "progress": 5,
            "stage": "init",
            "message": "初始化...",
        }

        pipeline = VideoPipeline()
        pages = picture_book_data.get("pages", [])
        total_pages = len(pages)

        def on_progress(progress):
            """进度回调 - 视频进度分配:
            - init: 0-5%
            - video_clips: 5-85% (按片段数量均分)
            - concat: 85-95%
            - save: 95-100%
            """
            stage_code = progress.stage
            current = progress.current
            total = progress.total

            if stage_code == "video_clips":
                # 视频片段生成: 5-85%，每个片段均分
                stage = f"clip_{current}" if current > 0 else "clip_1"
                base_progress = 5
                stage_range = 80  # 5-85%
                calculated_progress = base_progress + int(stage_range * current / max(total, 1))
                message = f"正在生成第 {current}/{total} 个视频片段..."
            elif stage_code == "concat":
                stage = "concat"
                calculated_progress = 90
                message = "正在拼接视频..."
            else:
                stage = stage_code
                calculated_progress = 50
                message = progress.message

            _task_status[task_id].update({
                "progress": calculated_progress,
                "stage": stage,
                "message": message,
            })

        _task_status[task_id].update({
            "progress": 10,
            "stage": "clip_1",
            "message": f"正在生成第 1/{total_pages} 个视频片段...",
        })

        result = await pipeline.generate(
            picture_book_data=picture_book_data,
            on_progress=on_progress,
        )

        _task_status[task_id].update({
            "progress": 95,
            "stage": "saving",
            "message": "保存到数据库...",
        })

        # 使用独立的数据库会话保存
        async with async_session_factory() as db:
            content_id = await save_content_to_db(
                db=db,
                title=result["title"],
                content_type=ContentType.VIDEO,
                theme_category=theme_category or "cognition",
                theme_topic=theme_topic or result["title"],
                personalization={"child_name": child_name} if child_name else {},
                content_data={
                    "video_url": result.get("video_url", ""),
                    "thumbnail_url": result.get("thumbnail_url", ""),
                    "clips": result.get("clips", []),
                },
                duration=int(result.get("duration", 0)),
                generated_by=result.get("generated_by", {}),
            )

        # 将 content_id 添加到结果中
        result["id"] = content_id

        _task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "stage": "completed",
            "message": "生成完成",
            "content_id": content_id,
            "result": result,
        }
        logger.info(f"Video task {task_id} completed, content_id={content_id}")

    except Exception as e:
        logger.exception(f"Video task {task_id} failed: {e}")
        _task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "stage": "failed",
            "message": "生成失败",
            "error": str(e),
        }


@router.post("/video/async", response_model=AsyncTaskResponse)
async def generate_video_async(
    request: VideoRequest,
):
    """异步生成视频，立即返回 task_id，前端轮询状态.

    这是推荐的调用方式，避免 Cloudflare 超时。
    视频生成通常需要 3-5 分钟，远超 Cloudflare 100 秒限制。

    Args:
        request: 视频生成请求，包含绘本数据

    Returns:
        task_id 用于轮询状态
    """
    task_id = str(uuid4())

    # 初始化任务状态
    _task_status[task_id] = {
        "status": "pending",
        "progress": 0,
        "stage": "pending",
        "message": "排队中...",
    }

    # 使用 asyncio.create_task 立即开始执行
    asyncio.create_task(
        _generate_video_background(
            task_id=task_id,
            picture_book_data=request.picture_book,
            child_name=request.child_name,
            theme_topic=request.theme_topic,
            theme_category=request.theme_category,
            motion_style=request.motion_style,
        )
    )

    return AsyncTaskResponse(
        task_id=task_id,
        status="pending",
        message="视频生成任务已创建，请轮询状态",
    )


@router.get("/video/status/{task_id}", response_model=TaskStatusResponse)
async def get_video_status(task_id: str):
    """查询视频生成任务状态.

    前端应每 3-5 秒轮询一次，直到 status 为 completed 或 failed。

    返回：
    - status: pending/processing/completed/failed
    - progress: 0-100 进度百分比
    - stage: 当前阶段 (clip_1, clip_2, ..., concat, saving, completed)
    - message: 人类可读消息
    - content_id: 完成后的内容 ID
    - result: 完成后的视频数据
    - error: 失败时的错误信息
    """
    if task_id not in _task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    status = _task_status[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=status.get("status", "unknown"),
        progress=status.get("progress", 0),
        stage=status.get("stage"),
        message=status.get("message"),
        content_id=status.get("content_id"),
        result=status.get("result"),
        error=status.get("error"),
    )


# ========== Standalone Video API ==========

async def _generate_standalone_video_background(
    task_id: str,
    request: StandaloneVideoRequest,
):
    """Background task for standalone video generation."""
    from moana.pipelines.standalone_video import StandaloneVideoPipeline
    from moana.models.content import Content, ContentType, ContentStatus

    try:
        pipeline = StandaloneVideoPipeline()

        def on_progress(progress):
            _task_status[task_id] = {
                "status": "processing",
                "progress": progress.progress,
                "stage": progress.stage,
                "message": progress.message,
            }

        result = await pipeline.generate(
            child_name=request.child_name,
            age_months=request.age_months,
            custom_prompt=request.custom_prompt,
            first_frame_url=request.first_frame_url,
            generate_first_frame=request.generate_first_frame,
            aspect_ratio=request.aspect_ratio,
            resolution=request.resolution,
            duration_seconds=request.duration_seconds,
            motion_mode=request.motion_mode,
            art_style=request.art_style,
            auto_enhance_prompt=request.auto_enhance_prompt,
            negative_prompt=request.negative_prompt,
            scene_template=request.scene_template,
            on_progress=on_progress,
        )

        # Save to database
        async with async_session_factory() as db:
            content_id = await save_content_to_db(
                db=db,
                title=result["title"],
                content_type=ContentType.VIDEO,
                theme_category=result["theme_category"],
                theme_topic=result["theme_topic"],
                personalization=result["personalization"],
                content_data={
                    "video_url": result["video_url"],
                    "thumbnail_url": result["thumbnail_url"],
                    "first_frame_url": result["first_frame_url"],
                    "custom_prompt": result["custom_prompt"],
                    "prompt_enhanced": result["prompt_enhanced"],
                    "creation_mode": "smart",
                },
                duration=int(result["duration"]),
                generated_by=result["generated_by"],
            )

            _task_status[task_id] = {
                "status": "completed",
                "progress": 100,
                "stage": "complete",
                "message": "生成完成",
                "content_id": content_id,
                "result": {
                    "id": content_id,
                    "title": result["title"],
                    "video_url": result["video_url"],
                    "thumbnail_url": result["thumbnail_url"],
                    "duration": result["duration"],
                },
            }

    except Exception as e:
        logger.error(f"Standalone video task {task_id} failed: {e}")
        _task_status[task_id] = {
            "status": "failed",
            "progress": 0,
            "stage": "failed",
            "message": "生成失败",
            "error": str(e),
        }


@router.post("/video/standalone/async", response_model=AsyncTaskResponse)
async def generate_standalone_video_async(request: StandaloneVideoRequest):
    """Generate standalone video from user prompt (async).

    Returns task_id immediately, poll /video/status/{task_id} for progress.

    Two modes for first frame:
    1. Provide first_frame_url - use existing image
    2. Set generate_first_frame=True - auto-generate with Gemini
    """
    import uuid

    task_id = f"standalone_video_{uuid.uuid4().hex[:12]}"

    _task_status[task_id] = {
        "status": "pending",
        "progress": 0,
        "stage": "init",
        "message": "排队中...",
    }

    asyncio.create_task(
        _generate_standalone_video_background(task_id, request)
    )

    return AsyncTaskResponse(
        task_id=task_id,
        status="pending",
        message="视频生成任务已创建，请轮询状态",
    )


@router.post("/video", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """同步生成视频（可能超时，建议使用 /video/async）.

    将绘本转换为带音频的动态视频。每张插图生成视频片段，
    然后拼接成完整视频。支持 MiniMax Hailuo 和阿里万相模型。
    """
    pipeline = VideoPipeline()

    try:
        result = await pipeline.generate(
            picture_book_data=request.picture_book,
        )

        # Save to database
        content_id = await save_content_to_db(
            db=db,
            title=result["title"],
            content_type=ContentType.VIDEO,
            theme_category=request.theme_category or "cognition",
            theme_topic=request.theme_topic or result["title"],
            personalization={"child_name": request.child_name} if request.child_name else {},
            content_data={
                "video_url": result.get("video_url", ""),
                "thumbnail_url": result.get("thumbnail_url", ""),
                "clips": result.get("clips", []),
            },
            duration=int(result.get("duration", 0)),
            generated_by=result.get("generated_by", {}),
        )

        # Add content_id to response
        result["id"] = content_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
