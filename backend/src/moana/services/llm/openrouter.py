# src/moana/services/llm/openrouter.py
"""OpenRouter LLM 服务.

OpenRouter 提供统一接口访问多种 LLM 模型（Claude, GPT, Llama 等）。
文档: https://openrouter.ai/docs
"""
import json
from typing import Type, TypeVar

import httpx
from pydantic import BaseModel

from moana.config import get_settings
from moana.services.llm.base import BaseLLMService

T = TypeVar("T", bound=BaseModel)


class OpenRouterService(BaseLLMService):
    """OpenRouter LLM 服务实现.

    支持通过 OpenRouter 访问多种模型：
    - anthropic/claude-3.5-sonnet
    - openai/gpt-4o
    - meta-llama/llama-3.1-70b-instruct
    等等
    """

    API_BASE = "https://openrouter.ai/api/v1"

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model
        self._site_url = settings.openrouter_site_url
        self._site_name = settings.openrouter_site_name

        if not self._api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouter service")

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """使用 OpenRouter 生成文本."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._site_url,
            "X-Title": self._site_name,
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.API_BASE}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            raise ValueError(f"OpenRouter error: {data['error']}")

        return data["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> T:
        """生成结构化输出."""
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)

        structured_prompt = f"""{prompt}

Please respond with a valid JSON object that matches this schema:
{schema_json}

Respond ONLY with the JSON object, no additional text or markdown."""

        full_system = system_prompt or ""
        full_system += "\nYou are a helpful assistant that responds in valid JSON format."

        response = await self.generate(
            prompt=structured_prompt,
            system_prompt=full_system,
            temperature=temperature,
        )

        # 解析 JSON
        json_str = response.strip()
        if json_str.startswith("```"):
            # 移除 markdown 代码块
            lines = json_str.split("\n")
            # 找到 JSON 开始和结束
            start_idx = 1 if lines[0].startswith("```") else 0
            end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            json_str = "\n".join(lines[start_idx:end_idx])

        data = json.loads(json_str)
        return output_schema.model_validate(data)
