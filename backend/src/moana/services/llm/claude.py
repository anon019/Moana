import json
from typing import Type, TypeVar
from anthropic import AsyncAnthropic
from pydantic import BaseModel

from moana.config import get_settings
from moana.services.llm.base import BaseLLMService

T = TypeVar("T", bound=BaseModel)


class ClaudeService(BaseLLMService):
    """Claude LLM service implementation."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

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
        """Generate text completion using Claude."""
        messages = [{"role": "user", "content": prompt}]

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text

    async def generate_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> T:
        """Generate structured output matching the given Pydantic schema."""
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)

        structured_prompt = f"""{prompt}

Please respond with a valid JSON object that matches this schema:
{schema_json}

Respond ONLY with the JSON object, no additional text."""

        full_system = system_prompt or ""
        full_system += "\nYou are a helpful assistant that responds in valid JSON format."

        response = await self.generate(
            prompt=structured_prompt,
            system_prompt=full_system,
            temperature=temperature,
        )

        # Parse and validate
        json_str = response.strip()
        if json_str.startswith("```"):
            # Remove markdown code blocks if present
            lines = json_str.split("\n")
            json_str = "\n".join(lines[1:-1])

        data = json.loads(json_str)
        return output_schema.model_validate(data)
