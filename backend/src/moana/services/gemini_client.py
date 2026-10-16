"""Google Gemini / Vertex AI 的统一禁用入口，禁止创建付费客户端。"""


class GoogleProviderDisabledError(ValueError):
    """用户已停用全部 Google 生成后端，不允许自动恢复或回退。"""


def get_gemini_client(location: str | None = None, *, retry_attempts: int | None = None):
    """保留旧调用签名，在读取凭据和建立连接之前失败关闭。"""
    raise GoogleProviderDisabledError(
        "Gemini、Vertex AI、Imagen 和 Veo 已停用，禁止发起 Google 模型请求。"
        "文本请使用 Codex CLI 的 gpt-6-luna；图片、语音和视频需另行配置已获授权的后端。"
    )
