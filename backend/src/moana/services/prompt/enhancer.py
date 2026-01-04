# src/moana/services/prompt/enhancer.py
"""Prompt enhancement service using Gemini for Suno music generation.

V2 redesign:
- 支持 31+ 动态参数
- 生成 Suno V5 专用提示词（英文+风格标签）
- 500 字符限制优化
- 支持 HTTP 代理
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai
import httpx

from moana.config import get_settings
from moana.services.prompt.templates import build_preset_template, build_smart_template

logger = logging.getLogger(__name__)


def _get_proxy_url() -> Optional[str]:
    """Get proxy URL from environment variables."""
    return os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("ALL_PROXY")


# Suno V5 专用系统提示词 - 重点强化主题创意
SUNO_ENHANCE_SYSTEM_PROMPT = """你是 Suno V5 儿歌提示词专家。

## 核心任务
根据用户的主题和创意，生成丰富、生动的 Suno 音乐提示词。

## ⚠️ 最重要规则
1. **重点强化 theme_topic 和 custom_prompt**：
   - 深入挖掘主题内涵，添加生动的场景描述
   - 扩展用户创意，加入适合儿童的故事元素
   - 让歌曲主题更加具体、有画面感
2. 其他参数做解释性转换即可，确保每个参数都体现
3. **禁止在输出中出现任何人名**

## 主题强化示例
- 用户输入 "刷牙" → "A cheerful morning routine song about brushing teeth with sparkly toothpaste, making bubbles, counting teeth, and smiling in the mirror"
- 用户输入 "睡觉" → "A gentle bedtime lullaby about the moon and stars, soft blankets, teddy bears, and sweet dreams floating in the night sky"
- 用户输入 "吃饭" → "A fun mealtime song about yummy vegetables, colorful fruits, using chopsticks, and growing strong and healthy"

## 参数映射规则（30个参数，不含 child_name）

### 主题参数（重点强化）
- theme_topic → 深入扩展主题，添加场景、动作、情感元素
- theme_category → habit=日常习惯场景, cognition=学习探索场景, motor=运动游戏场景
- custom_prompt → 保留用户创意核心，丰富细节和画面感

### 年龄适配
- age_months → 0-24="for babies, very simple", 24-36="for toddlers", 36-48="for preschoolers", 48+="for young children"

### 音乐风格（解释性转换）
- music_mood → [Cheerful], [Gentle], [Playful], [Lullaby], [Educational], [Rhythmic], [Soothing], [Festive]
- music_genre → children, pop, folk, classical, electronic, world, jazz
- tempo → "tempo X BPM"
- energy_level → 1-3=calm, 4-6=moderate, 7-10=energetic

### 人声设置（解释性转换）
- vocal_type → soft_female, energetic_female, soft_male, child_voice, child_chorus, duet
- vocal_range → high-pitched, mid-range, low voice
- vocal_emotion → happy, tender, excited, calm, playful, warm
- vocal_style → clear, breathy, powerful
- vocal_effects → reverb, echo, harmony
- vocal_regional → Chinese style, Cantonese accent

### 乐器与音效
- instruments → 直接列出
- sound_effects → 直接列出

### 歌词与结构
- lyric_complexity → simple/moderate/rich words
- repetition_level → varied/moderate/highly repetitive
- song_structure → verse-chorus/simple AABB/extended
- duration_preference → short/medium/full length
- action_types → with clapping/danceable/with jumping

### 语言文化（重要）
- language → Chinese lyrics / English lyrics / bilingual Chinese-English
- cultural_style → modern Chinese / traditional Chinese / Western style

### 其他参数
- educational_focus, favorite_characters, favorite_colors → 自然融入描述
- style_weight, creativity, negative_tags, style_description → 按值转换

## 输出格式
1. **≤ 400 字符**（Suno API 限制 500 字符，预留缓冲）
2. 此提示词作为核心创意，Suno 将根据它自动生成歌词（不严格匹配输入）
3. 格式：[风格标签] + 丰富的主题描述 + 语言 + 人声 + 乐器 + 节奏 + 特色
4. **禁止出现任何人名**
5. 英文书写，主题可保留中文
6. 直接输出，不要解释

## 输出示例
[Cheerful Children's Pop] A fun morning song about brushing teeth - making foamy bubbles, counting to twenty, seeing a sparkly smile in the mirror. Chinese lyrics. Soft female vocal, happy and encouraging. Piano, xylophone, giggle sounds. Tempo 110 BPM, high energy. Simple repetitive chorus with clapping.

[Gentle Lullaby] A dreamy bedtime song about floating on clouds, watching twinkling stars, and cuddling with a soft teddy bear. Bilingual Chinese-English. Child vocal, tender and soothing. Music box, gentle bells. Slow tempo 70 BPM, calm and peaceful."""


@dataclass
class EnhanceResult:
    """Result of prompt enhancement."""
    template_prompt: str      # Original template (Chinese)
    enhanced_prompt: str      # Suno-optimized prompt (English)
    model: str               # Model used
    duration_ms: int         # Enhancement duration


class PromptEnhancer:
    """Prompt enhancement service using Gemini.

    Enhances user parameters into Suno V5 optimized prompts.
    Supports 31+ dynamic parameters with automatic template generation.
    """

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        # Use gemini-3-flash-preview for best parameter understanding (2025-12-17 release)
        self._model_name = model_name or "gemini-3-flash-preview"

        # Configure Gemini with proxy support
        proxy_url = _get_proxy_url()
        if proxy_url:
            logger.info(f"Using proxy for Gemini API: {proxy_url}")
            # Create httpx client with proxy
            http_client = httpx.Client(proxy=proxy_url, timeout=30.0)
            genai.configure(
                api_key=settings.google_api_key,
                transport="rest",  # Use REST transport for proxy support
            )
            self._http_client = http_client
        else:
            logger.warning("No proxy configured for Gemini API")
            genai.configure(api_key=settings.google_api_key)
            self._http_client = None

        self._model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=SUNO_ENHANCE_SYSTEM_PROMPT,
        )
        self._api_key = settings.google_api_key

    async def enhance(self, params: dict) -> EnhanceResult:
        """Enhance parameters into a Suno-optimized prompt.

        Args:
            params: Dictionary with all nursery rhyme parameters.
                   Supports 31+ parameters, all are optional except
                   child_name and age_months.

        Returns:
            EnhanceResult with template and enhanced prompts.
        """
        start_time = time.time()

        # Build template based on creation mode
        creation_mode = params.get("creation_mode", "preset")

        if creation_mode == "smart":
            template_prompt = build_smart_template(params)
        else:
            template_prompt = build_preset_template(params)

        logger.info(f"Template prompt ({len(template_prompt)} chars): {template_prompt[:100]}...")

        # Enhance with Gemini (use REST API with proxy)
        enhanced_prompt = await self._call_gemini_api(template_prompt)

        if not enhanced_prompt:
            logger.warning("Gemini API failed, using fallback prompt")
            enhanced_prompt = self._build_fallback_prompt(params)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Enhanced prompt ({len(enhanced_prompt)} chars, {duration_ms}ms): {enhanced_prompt[:100]}...")

        return EnhanceResult(
            template_prompt=template_prompt,
            enhanced_prompt=enhanced_prompt,
            model=self._model_name,
            duration_ms=duration_ms,
        )

    async def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call Gemini API directly with proxy support.

        Args:
            prompt: The prompt to send to Gemini.

        Returns:
            Enhanced prompt string or None if failed.
        """
        proxy_url = _get_proxy_url()

        # Gemini REST API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent"

        # Request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SUNO_ENHANCE_SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 250,
            }
        }

        try:
            async with httpx.AsyncClient(proxy=proxy_url, timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    params={"key": self._api_key},
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text[:200]}")
                    return None

                data = response.json()

                # Extract text from response
                candidates = data.get("candidates", [])
                if not candidates:
                    logger.error("Gemini API returned no candidates")
                    return None

                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if not parts:
                    logger.error("Gemini API returned no parts")
                    return None

                enhanced_prompt = parts[0].get("text", "").strip()

                # Clean up: remove markdown formatting if present
                if enhanced_prompt.startswith("```"):
                    lines = enhanced_prompt.split("\n")
                    enhanced_prompt = "\n".join(
                        line for line in lines
                        if not line.startswith("```")
                    ).strip()

                # Ensure within Suno limit (500 chars max, target ≤450)
                if len(enhanced_prompt) > 450:
                    truncated = enhanced_prompt[:447]
                    last_period = max(
                        truncated.rfind("."),
                        truncated.rfind("。"),
                        truncated.rfind(","),
                    )
                    if last_period > 300:
                        enhanced_prompt = truncated[:last_period + 1]
                    else:
                        enhanced_prompt = truncated + "..."
                    logger.warning(f"Enhanced prompt truncated to {len(enhanced_prompt)} chars")

                return enhanced_prompt

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    def _build_fallback_prompt(self, params: dict) -> str:
        """Build a simple fallback prompt when Gemini fails.

        Args:
            params: Dictionary with all parameters.

        Returns:
            Basic Suno prompt string (no child_name included).
        """
        theme_topic = params.get("theme_topic", "儿歌")
        music_mood = params.get("music_mood", "cheerful")
        vocal_type = params.get("vocal_type", params.get("vocal_gender", "female"))
        language = params.get("language", "chinese")

        # Map Chinese mood to English
        mood_map = {
            "cheerful": "cheerful",
            "gentle": "gentle",
            "playful": "playful",
            "lullaby": "lullaby",
            "educational": "educational",
            "rhythmic": "rhythmic",
            "soothing": "soothing",
            "festive": "festive",
        }
        mood_en = mood_map.get(music_mood, "cheerful")

        # Map vocal type
        vocal_map = {
            "soft_female": "soft female vocal",
            "energetic_female": "energetic female vocal",
            "soft_male": "soft male vocal",
            "child_voice": "child vocal",
            "child_chorus": "children's choir",
            "duet": "duet vocal",
        }
        vocal_en = vocal_map.get(vocal_type, "soft female vocal")

        # Map language
        lang_map = {
            "chinese": "Chinese lyrics",
            "english": "English lyrics",
            "mixed": "bilingual Chinese-English lyrics",
        }
        lang_en = lang_map.get(language, "Chinese lyrics")

        # Build instruments string
        instruments = params.get("instruments", [])
        if instruments:
            instruments_str = ", ".join(instruments[:3])
        else:
            instruments_str = "piano, xylophone"

        prompt = (
            f"[{mood_en.title()} Children's Song] "
            f"A fun nursery rhyme about {theme_topic}. "
            f"{lang_en}. {vocal_en.title()}, warm and engaging. "
            f"{instruments_str.title()}. "
            f"Catchy melody, easy to sing along."
        )

        return prompt[:450]  # Ensure under Suno 500 char limit
