# src/moana/models/generation_log.py
"""生成过程日志模型.

记录每次内容生成的详细步骤和参数，便于排查问题和分析性能。
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, JSON, ForeignKey, Integer, Float, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

from moana.models.base import Base, TimestampMixin


class LogLevel(str, Enum):
    """日志级别."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class GenerationStep(str, Enum):
    """生成步骤类型."""
    # 通用步骤
    INIT = "init"  # 初始化
    VALIDATE = "validate"  # 参数验证

    # 故事生成
    STORY_GENERATE = "story_generate"  # 生成故事大纲
    STORY_ENHANCE = "story_enhance"  # 故事增强

    # 图片生成
    IMAGE_PROMPT = "image_prompt"  # 生成图片提示词
    IMAGE_GENERATE = "image_generate"  # 生成图片
    IMAGE_UPLOAD = "image_upload"  # 上传图片

    # 音频生成
    AUDIO_SYNTHESIZE = "audio_synthesize"  # 语音合成
    AUDIO_UPLOAD = "audio_upload"  # 上传音频

    # 提示词增强 (nursery rhyme redesign)
    PROMPT_ENHANCE = "prompt_enhance"  # Gemini 提示词增强
    PROMPT_TEMPLATE = "prompt_template"  # 模板组装

    # 音乐生成
    MUSIC_LYRICS = "music_lyrics"  # 生成歌词
    MUSIC_GENERATE = "music_generate"  # 生成音乐
    MUSIC_CALLBACK = "music_callback"  # 音乐回调

    # 视频生成
    VIDEO_FIRST_FRAME = "video_first_frame"  # 生成首帧
    VIDEO_GENERATE = "video_generate"  # 生成视频
    VIDEO_UPLOAD = "video_upload"  # 上传视频

    # 后处理
    SAVE_TO_DB = "save_to_db"  # 保存到数据库
    MODERATION = "moderation"  # 内容审核
    COMPLETE = "complete"  # 完成


class GenerationLog(Base, TimestampMixin):
    """生成过程日志记录.

    每条记录代表一个生成步骤，包含输入参数、输出结果、耗时和错误信息。
    """

    __tablename__ = "generation_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # 关联的任务 ID（异步任务 ID）
    task_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # 关联的内容 ID（生成完成后填充）
    content_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("contents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 生成步骤
    step: Mapped[GenerationStep] = mapped_column(
        SQLEnum(GenerationStep, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    # 日志级别
    level: Mapped[LogLevel] = mapped_column(
        SQLEnum(LogLevel, values_callable=lambda x: [e.value for e in x]),
        default=LogLevel.INFO,
        nullable=False,
    )

    # 步骤序号（同一任务内的顺序）
    sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 消息摘要
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    # 输入参数（JSON）
    input_params: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # 输出结果（JSON）
    output_result: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # 耗时（秒）
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 错误堆栈
    error_traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 额外元数据
    extra_data: Mapped[dict] = mapped_column(
        "extra_data",
        JSON,
        default=dict,
        nullable=False,
    )
