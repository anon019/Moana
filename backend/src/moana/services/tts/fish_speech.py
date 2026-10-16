"""历史 Fish provider 名称兼容层；只允许固定免费模型 CLI。"""

from moana.services.tts.fish_cli import FishFreeCLIService


class FishSpeechService(FishFreeCLIService):
    """兼容旧配置，免费截止后拒绝请求，绝不回退付费模型。"""
