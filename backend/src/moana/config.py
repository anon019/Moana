from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://moana:your_password@localhost:5432/moana"

    # === Provider 选择（运行时可切换） ===
    # LLM 支持: gemini (原生) | openrouter (多模型) | claude
    llm_provider: str = "gemini"  # gemini | openrouter | claude
    image_provider: str = "gemini"  # gemini | wanx | imagen | minimax | qwen | flux
    tts_provider: str = "gemini"  # gemini | qwen | minimax | fish_speech
    music_provider: str = "suno"  # suno | minimax
    video_provider: str = "veo"  # veo | wanx | minimax

    # === LLM - Google Gemini (原生 API，主力) ===
    # 可用模型: gemini-3-pro-preview | gemini-3-flash-preview | gemini-2.5-flash
    google_api_key: str = ""
    google_model: str = "gemini-3-flash-preview"

    # === LLM - Anthropic Claude (原生 API，备选) ===
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # === LLM - OpenRouter (多模型网关，推荐) ===
    # 支持的模型 (2025年12月最新):
    # - anthropic/claude-4.5-sonnet (最新最强，推荐)
    # - anthropic/claude-4.5-opus (最强推理)
    # - google/gemini-2.5-flash (快速便宜)
    # - google/gemini-3-pro-preview (Gemini 3 预览)
    # - openai/gpt-5 (OpenAI 旗舰)
    # - x-ai/grok-4.1-fast (Grok 4.1)
    # - deepseek/deepseek-chat-v3-0324 (DeepSeek V3，便宜)
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-4.5-sonnet"
    openrouter_site_url: str = "https://example.com"
    openrouter_site_name: str = "Kids Early Education"

    # === 阿里云 DashScope (Qwen 系列 + 万相) ===
    dashscope_api_key: str = ""
    dashscope_api_base: str = "https://dashscope.aliyuncs.com/api/v1"
    # Qwen LLM (备选)
    qwen_llm_model: str = "qwen3-max-preview"
    # Qwen 图像生成 (备选)
    qwen_image_model: str = "qwen-image-plus"
    # Qwen TTS (主力)
    qwen_tts_model: str = "qwen3-tts-flash-realtime"
    # 阿里万相图片 (主力) - wan2.6-t2i 支持同步接口
    wanx_image_model: str = "wan2.6-t2i"
    # 阿里万相视频 (主力) - wan2.6-i2v 支持有声+多镜头
    wanx_video_model: str = "wan2.6-i2v"
    wanx_video_resolution: str = "720P"  # 720P/1080P
    wanx_video_duration: int = 5  # 5/10/15秒

    # === MiniMax ===
    minimax_api_key: str = ""
    minimax_api_base: str = "https://api.minimaxi.com"
    # MiniMax 音乐 (主力)
    minimax_music_model: str = "music-2.0"
    # MiniMax 图像 (主力)
    minimax_image_model: str = "image-01"
    # MiniMax TTS (备选)
    minimax_tts_model: str = "speech-2.6-turbo"
    # MiniMax 视频 (备选)
    minimax_video_model: str = "Hailuo-2.3-Fast"

    # === Flux 图像生成 (备选) ===
    flux_api_key: str = ""
    flux_api_base: str = "https://api.bfl.ml"

    # === Midjourney (预留) ===
    midjourney_api_key: str = ""
    midjourney_api_base: str = "https://api.midjourney.com"

    # === TTS - Fish Speech (备选) ===
    fish_speech_api_key: str = ""
    fish_speech_api_base: str = "https://api.fish.audio"

    # === Suno 音乐 (主力) - sunoapi.org ===
    suno_api_key: str = ""
    suno_api_base: str = "https://api.sunoapi.org"
    suno_model: str = "V5"

    # === Google Gemini 图像生成 (Nano Banana Pro，主力) ===
    gemini_image_model: str = "gemini-3-pro-image-preview"

    # === Google Gemini TTS (语音合成，主力) ===
    gemini_tts_model: str = "gemini-2.5-flash-preview-tts"
    gemini_tts_voice: str = "Kore"  # 默认音色，适合儿童内容

    # === Google Imagen 4 (图片生成，备选) ===
    # Available models: imagen-4.0-generate-001, imagen-4.0-fast-generate-001, imagen-4.0-ultra-generate-001
    # fast: faster generation, good for batch operations
    # ultra: higher quality, better prompt alignment
    imagen_model: str = "imagen-4.0-fast-generate-001"

    # === Google Veo 3.1 (视频生成，主力) ===
    # Available: veo-3.1-generate-preview (standard), veo-3.1-fast-generate-preview (fast)
    veo_model: str = "veo-3.1-generate-preview"
    veo_resolution: str = "720p"
    veo_duration: int = 8

    # === Storage ===
    # Storage provider: local | oss
    storage_provider: str = "local"

    # Local storage (recommended for personal use)
    storage_local_path: str = "/var/www/kids/media"
    storage_base_url: str = "https://example.com/media"

    # Aliyun OSS (for production scale)
    oss_access_key: str = ""
    oss_secret_key: str = ""
    oss_bucket: str = "moana-content"
    oss_endpoint: str = ""

    # === WeChat OAuth ===
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # === JWT Auth ===
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # === App settings ===
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
