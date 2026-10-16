# src/moana/services/llm/gemini.py
"""Google Gemini LLM 服务.

使用新版 google-genai SDK，支持 Vertex AI / API Key 双模式。
"""
import json
import re
from typing import Type, TypeVar

from google.genai import types
from pydantic import BaseModel

from moana.config import get_settings
from moana.services.gemini_client import get_gemini_client
from moana.services.llm.base import BaseLLMService

T = TypeVar("T", bound=BaseModel)


class GeminiService(BaseLLMService):
    """Google Gemini LLM 服务实现.

    使用 Gemini 3 Pro 作为主力模型。
    文档: https://ai.google.dev/gemini-api/docs
    """

    def __init__(self, *, retry_attempts: int | None = None):
        settings = get_settings()
        self._model_name = settings.google_model
        self._client = (
            get_gemini_client(retry_attempts=retry_attempts)
            if retry_attempts is not None else get_gemini_client()
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """使用 Gemini 生成文本."""
        # 配置生成参数
        # 注意: gemini-3-flash-preview / gemini-3.1-pro-preview 需要 max_output_tokens >= 1000
        # 可能是因为内部思考链机制需要预留 token 空间
        effective_max_tokens = max(max_tokens, 1000)

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=effective_max_tokens,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
            ],
        )

        # 使用 SDK 的 system_instruction 参数
        if system_prompt:
            config.system_instruction = system_prompt

        # 使用异步 SDK 调用
        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=config,
        )

        # 处理安全过滤的情况
        if not response.candidates or not response.candidates[0].content.parts:
            finish_reason = (
                response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
            )
            raise ValueError(f"Gemini response blocked (finish_reason={finish_reason})")

        return response.text

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

IMPORTANT:
- Respond ONLY with the JSON object
- Do NOT include markdown code blocks
- Ensure all strings are properly escaped (use \\n for newlines, \\" for quotes)
- The response must be complete and valid JSON"""

        full_system = system_prompt or ""
        full_system += "\nYou are a helpful assistant that responds in valid JSON format only."

        # 使用更大的 max_tokens 确保 JSON 不被截断
        response = await self.generate(
            prompt=structured_prompt,
            system_prompt=full_system,
            temperature=temperature,
            max_tokens=8192,  # 增加 token 限制避免截断
        )

        # 健壮地解析 JSON
        json_str = self._extract_json(response)
        data = json.loads(json_str)
        return output_schema.model_validate(data)

    def _extract_json(self, text: str) -> str:
        """从响应文本中提取 JSON 字符串.

        处理各种边缘情况：
        - markdown 代码块
        - 前后的额外文本
        - 不完整的 JSON（尝试修复）
        """
        text = text.strip()

        # 1. 移除 markdown 代码块标记
        # 匹配 ```json 或 ``` 开头和结尾
        code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        # 2. 如果仍然有 ``` 开头但没有结尾（截断情况）
        if text.startswith("```"):
            lines = text.split("\n")
            # 跳过第一行（```json 或 ```）
            text = "\n".join(lines[1:]).strip()

        # 3. 尝试提取 JSON 对象（从第一个 { 到最后一个 }）
        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]
        elif first_brace != -1 and last_brace == -1:
            # JSON 被截断，尝试修复
            text = text[first_brace:]
            text = self._try_fix_truncated_json(text)

        return text

    def _try_fix_truncated_json(self, json_str: str) -> str:
        """尝试修复被截断的 JSON.

        这是一个尽力修复的方法，可能不总是成功。
        """
        # 计算未闭合的括号
        open_braces = json_str.count("{") - json_str.count("}")
        open_brackets = json_str.count("[") - json_str.count("]")

        # 检查是否在字符串中间被截断
        # 简单策略：如果最后一个非空白字符是引号或逗号之外的字符
        # 可能需要先闭合字符串
        stripped = json_str.rstrip()

        # 检查未闭合的字符串
        in_string = False
        escape_next = False
        for char in stripped:
            if escape_next:
                escape_next = False
                continue
            if char == "\\":
                escape_next = True
                continue
            if char == '"':
                in_string = not in_string

        # 如果在字符串中间被截断
        if in_string:
            json_str = stripped + '"'

        # 闭合数组
        json_str += "]" * open_brackets

        # 闭合对象
        json_str += "}" * open_braces

        return json_str
