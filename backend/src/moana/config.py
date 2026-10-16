from functools import lru_cache
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://moana:moana123@localhost:5432/moana"

    # === Provider 选择（运行时可切换） ===
    # 文本使用现有 Codex 登录；Google 后端统一禁用。
    llm_provider: str = "codex"  # codex | gemini | openrouter | claude
    codex_model: str = "gpt-6-luna"
    codex_timeout: float = 180.0
    image_provider: str = "codex"  # codex | disabled | wanx | minimax | qwen | flux
    codex_image_model: str = "gpt-image-2.5-sunburst"
    codex_image_timeout: float = 240.0
    codex_image_isolate: bool = True  # 独立 systemd worker，避免挤占 API 后端 300MiB 上限。
    tts_provider: str = "fish_free_cli"  # fish_free_cli | disabled
    music_provider: str = "suno"  # suno | minimax
    video_provider: str = "disabled"  # disabled | wanx | minimax

    # === Google 历史配置（已停用，保留缓存兼容字段） ===
    google_model: str = "gemini-3-flash-preview"

    # === LLM - Anthropic Claude (原生 API，备选) ===
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # === LLM - OpenRouter（仅保留非 Google 兼容接口） ===
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-4.5-sonnet"
    openrouter_site_url: str = "http://localhost:3000"
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

    # === TTS - Fish Audio 免费在线托管 ===
    fish_speech_api_key: str = ""
    fish_speech_api_base: str = "https://api.fish.audio"
    fish_speech_voice_id: str = "cfe763b758ea496882bfae05808eb0c1"

    # Fish 免费托管语音，通过短生命周期 CLI 调用。
    tts_cli_python: str = sys.executable
    tts_cli_timeout: float = 120.0

    # === Suno 音乐 (主力) - sunoapi.org ===
    suno_api_key: str = ""
    suno_api_base: str = "https://api.sunoapi.org"
    suno_model: str = "V5"

    # === 已禁用的历史 Google 图片配置（仅供记录兼容） ===
    gemini_image_model: str = "gemini-3.1-flash-image"

    # === 已禁用的历史 Google TTS 配置 ===
    gemini_tts_model: str = "gemini-3.1-flash-tts-preview"
    gemini_tts_voice: str = "Kore"  # 默认音色，适合儿童内容

    # === 已禁用的历史 Google 视频配置 ===
    # Vertex AI GA model ID; preview endpoint was discontinued in 2026-04.
    veo_model: str = "veo-3.1-generate-001"
    # Veo predictLongRunning 使用区域端点，不复用 Gemini 的 global 端点。
    veo_location: str = "us-central1"
    veo_resolution: str = "720p"
    veo_duration: int = 8

    # === Storage ===
    # Storage provider: local | oss
    storage_provider: str = "local"

    # Local storage (recommended for personal use)
    storage_local_path: str = "./media"
    storage_base_url: str = "http://localhost:8080/media"
    callback_base_url: str = "http://localhost:8080"

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
    # Security and runtime
    jwt_secret_min_length: int = 32
    allowed_cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = False
    auto_init_db: bool = False

    # Task status persistence
    task_status_ttl_seconds: int = 30 * 60
    task_status_cleanup_interval_seconds: int = 5 * 60
    task_status_max_finished: int = 100

    # Sharing / admin config
    admin_openid: str = "admin_web_panel"
    admin_nickname: str = "管理员"
    mock_login_enabled: bool = False

    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
