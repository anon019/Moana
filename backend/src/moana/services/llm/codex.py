"""使用现有 Codex 订阅进行纯文本生成，不接管图像或语音端点。"""

import asyncio
import json
import re
from typing import TypeVar

from pydantic import BaseModel

from moana.config import get_settings
from moana.services.llm.base import BaseLLMService
from moana.services.llm.codex_client import CodexClient

T = TypeVar("T", bound=BaseModel)
_generation_lock = asyncio.Lock()


def parse_json_response(text: str) -> dict:
    """接受完整 JSON 或代码围栏，拒绝截断结果及非对象结果。"""
    text = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("文本模型必须返回完整 JSON 对象")
    return result


class CodexService(BaseLLMService):
    """串行、限时、可取消的 Codex 文本服务。"""

    def __init__(self):
        settings = get_settings()
        self._model_name = settings.codex_model
        self._timeout = settings.codex_timeout
        self._client = CodexClient()

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(
        self, prompt: str, system_prompt: str | None = None,
        temperature: float = 0.7, max_tokens: int = 4096,
    ) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("文本生成提示词不能为空")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        # CLI 不提供 temperature/max_tokens；篇幅由调用方提示词约束。
        async with asyncio.timeout(self._timeout):
            async with _generation_lock:
                response = await self._client.create(
                    model=self._model_name, messages=messages, timeout=self._timeout,
                )
        return response.choices[0].message.content

    async def generate_structured(
        self, prompt: str, output_schema: type[T],
        system_prompt: str | None = None, temperature: float = 0.7,
    ) -> T:
        schema = json.dumps(output_schema.model_json_schema(), ensure_ascii=False)
        response = await self.generate(
            prompt=f"{prompt}\n\n只返回符合以下 JSON Schema 的完整 JSON 对象：\n{schema}",
            system_prompt=system_prompt, temperature=temperature,
        )
        return output_schema.model_validate(parse_json_response(response))
