import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from moana.pipelines.picture_book import (
    GenerationRequest,
    ProtagonistConfig,
    StoryEnhancementConfig,
    VisualEnhancementConfig,
)


@pytest.mark.asyncio
async def test_picture_book_pipeline_initialization():
    """Test pipeline can be initialized."""
    from moana.pipelines.picture_book import PictureBookPipeline

    pipeline = PictureBookPipeline()
    assert pipeline is not None


@pytest.mark.asyncio
async def test_picture_book_pipeline_generate():
    """Test pipeline can generate a complete picture book."""
    from moana.pipelines.picture_book import PictureBookPipeline
    from moana.agents.schemas import PictureBookOutline, PictureBookPage
    from moana.services.image.base import ImageResult
    from moana.services.tts.base import TTSResult

    mock_outline = PictureBookOutline(
        title="小莫学刷牙",
        theme_topic="刷牙",
        educational_goal="养成刷牙习惯",
        pages=[
            PictureBookPage(
                page_num=1,
                text="早上起床啦！",
                image_prompt="A girl waking up",
                interaction=None,
            )
        ],
        total_interactions=0,
    )

    mock_image = ImageResult(
        url="https://example.com/image.png",
        prompt="test",
        model="flux",
    )

    mock_tts = TTSResult(
        audio_url="https://example.com/audio.mp3",
        duration=3.0,
        voice_id="test",
        model="fish",
    )

    with patch("moana.pipelines.picture_book.StoryAgent") as MockAgent, \
         patch("moana.pipelines.picture_book.get_image_service") as MockGetImage, \
         patch("moana.pipelines.picture_book.get_tts_service") as MockGetTTS:

        MockAgent.return_value.generate_outline = AsyncMock(return_value=mock_outline)
        MockAgent.return_value._llm = MagicMock(model_name="test-model")
        MockGetImage.return_value.generate = AsyncMock(return_value=mock_image)
        MockGetTTS.return_value.synthesize = AsyncMock(return_value=mock_tts)

        pipeline = PictureBookPipeline()
        result = await pipeline.generate(
            child_name="小莫",
            age_months=22,
            theme_topic="刷牙",
            theme_category="habit",
        )

        assert result["title"] == "小莫学刷牙"
        assert len(result["pages"]) == 1
        assert result["pages"][0]["image_url"] == "https://example.com/image.png"
        assert result["pages"][0]["audio_voice_id"] == "test"
        assert result["pages"][0]["audio_model"] == "fish"
        assert result["generated_by"]["tts_voice_id"] == "test"


@pytest.mark.asyncio
async def test_picture_book_generates_text_then_media_one_request_at_a_time():
    from moana.pipelines.picture_book import PictureBookPipeline
    from moana.agents.schemas import PictureBookOutline, PictureBookPage
    from moana.services.image.base import ImageResult
    from moana.services.tts.base import TTSResult

    events = []
    active = 0
    max_active = 0
    outline = PictureBookOutline(
        title="逐页绘本",
        theme_topic="测试",
        educational_goal="测试顺序",
        pages=[
            PictureBookPage(page_num=i, text=f"text-{i}", image_prompt=f"scene-{i}", interaction=None)
            for i in range(1, 4)
        ],
        total_interactions=0,
    )

    async def generate_outline(**_):
        events.append("text")
        return outline

    async def generate_image(*, prompt, **_):
        nonlocal active, max_active
        page = next(i for i in range(1, 4) if f"scene-{i}" in prompt)
        active += 1
        max_active = max(max_active, active)
        events.append(f"image-{page}")
        await asyncio.sleep(0)
        active -= 1
        return ImageResult(url=f"https://example.com/image-{page}.png", prompt=prompt, model="test")

    async def synthesize(*, text, **_):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        events.append(f"audio-{text[-1]}")
        await asyncio.sleep(0)
        active -= 1
        return TTSResult(audio_url=f"https://example.com/audio-{text[-1]}.mp3", duration=1.0, voice_id="test", model="test")

    with patch("moana.pipelines.picture_book.StoryAgent") as agent, \
         patch("moana.pipelines.picture_book.get_image_service") as images, \
         patch("moana.pipelines.picture_book.get_tts_service") as audio:
        agent.return_value.generate_outline = generate_outline
        agent.return_value._llm = MagicMock(model_name="test")
        images.return_value.generate = generate_image
        audio.return_value.synthesize = synthesize
        result = await PictureBookPipeline().generate(
            child_name="小莫", age_months=30, theme_topic="测试", theme_category="test",
        )

    assert events == ["text", "image-1", "image-2", "image-3", "audio-1", "audio-2", "audio-3"]
    assert max_active == 1
    assert len(result["pages"]) == 3


@pytest.mark.asyncio
async def test_picture_book_requests_share_one_generation_slot():
    from moana.pipelines.picture_book import PictureBookPipeline

    active = 0
    max_active = 0

    async def generate_one(_request):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0)
        active -= 1
        return {}

    first = PictureBookPipeline(story_agent=object(), image_service=object(), tts_service=object())
    second = PictureBookPipeline(story_agent=object(), image_service=object(), tts_service=object())
    request = GenerationRequest(child_name="小莫", age_months=30, theme_topic="测试", theme_category="test")
    with patch.object(PictureBookPipeline, "_generate_from_request", side_effect=generate_one):
        await asyncio.gather(first.generate(request=request), second.generate(request=request))

    assert max_active == 1


def test_generation_request_creation():
    """Test GenerationRequest can be created with required parameters."""
    request = GenerationRequest(
        child_name="小明",
        age_months=24,
        theme_topic="刷牙",
        theme_category="habit",
    )
    assert request.child_name == "小明"
    assert request.age_months == 24
    assert request.art_style == "pixar_3d"  # default
    assert request.color_palette == "pastel"  # default
    assert request.protagonist is None  # optional


def test_generation_request_with_protagonist():
    """Test GenerationRequest with protagonist configuration."""
    request = GenerationRequest(
        child_name="小明",
        age_months=24,
        theme_topic="刷牙",
        theme_category="habit",
        protagonist=ProtagonistConfig(
            animal="bear",
            color="brown",
            accessory="red scarf",
        ),
    )
    assert request.protagonist is not None
    assert request.protagonist.animal == "bear"
    assert request.protagonist.color == "brown"
    assert request.protagonist.accessory == "red scarf"


def test_generation_request_from_legacy_params():
    """Test creating GenerationRequest from legacy individual parameters."""
    request = GenerationRequest.from_legacy_params(
        child_name="小明",
        age_months=24,
        theme_topic="刷牙",
        theme_category="habit",
        art_style="watercolor",
        protagonist_animal="cat",
        protagonist_color="orange",
        protagonist_accessory="bow tie",
        color_palette="vibrant",
    )

    assert request.child_name == "小明"
    assert request.art_style == "watercolor"
    assert request.color_palette == "vibrant"
    assert request.protagonist is not None
    assert request.protagonist.animal == "cat"
    assert request.protagonist.color == "orange"
    assert request.protagonist.accessory == "bow tie"


def test_generation_request_to_style_config():
    """Test converting GenerationRequest to StyleConfig."""
    request = GenerationRequest(
        child_name="小明",
        age_months=24,
        theme_topic="刷牙",
        theme_category="habit",
        art_style="anime",
        color_palette="cool",
        protagonist=ProtagonistConfig(
            animal="fox",
            color="red",
            accessory="blue bandana",
        ),
    )

    style_config = request.to_style_config()

    assert style_config.art_style == "anime"
    assert style_config.color_palette == "cool"
    assert style_config.protagonist_animal == "fox"
    assert style_config.protagonist_color == "red"
    assert style_config.protagonist_accessory == "blue bandana"


def test_generation_request_with_enhancements():
    """Test GenerationRequest with story and visual enhancements."""
    request = GenerationRequest(
        child_name="小明",
        age_months=24,
        theme_topic="刷牙",
        theme_category="habit",
        story_enhancement=StoryEnhancementConfig(
            narrative_pace="slow",
            educational_focus="health",
        ),
        visual_enhancement=VisualEnhancementConfig(
            time_atmosphere="morning",
            emotional_tone="happy",
        ),
    )

    assert request.story_enhancement is not None
    assert request.story_enhancement.narrative_pace == "slow"
    assert request.story_enhancement.educational_focus == "health"
    assert request.visual_enhancement is not None
    assert request.visual_enhancement.time_atmosphere == "morning"
    assert request.visual_enhancement.emotional_tone == "happy"


@pytest.mark.asyncio
async def test_picture_book_pipeline_generate_with_request_object():
    """Test pipeline can generate with GenerationRequest object."""
    from moana.pipelines.picture_book import PictureBookPipeline
    from moana.agents.schemas import PictureBookOutline, PictureBookPage
    from moana.services.image.base import ImageResult
    from moana.services.tts.base import TTSResult

    mock_outline = PictureBookOutline(
        title="小明学刷牙",
        theme_topic="刷牙",
        educational_goal="养成刷牙习惯",
        pages=[
            PictureBookPage(
                page_num=1,
                text="早上起床啦！",
                image_prompt="A bear waking up",
                interaction=None,
            )
        ],
        total_interactions=0,
    )

    mock_image = ImageResult(
        url="https://example.com/image.png",
        prompt="test",
        model="flux",
    )

    mock_tts = TTSResult(
        audio_url="https://example.com/audio.mp3",
        duration=3.0,
        voice_id="test",
        model="fish",
    )

    with patch("moana.pipelines.picture_book.StoryAgent") as MockAgent, \
         patch("moana.pipelines.picture_book.get_image_service") as MockGetImage, \
         patch("moana.pipelines.picture_book.get_tts_service") as MockGetTTS:

        MockAgent.return_value.generate_outline = AsyncMock(return_value=mock_outline)
        MockAgent.return_value._llm = MagicMock(model_name="test-model")
        MockGetImage.return_value.generate = AsyncMock(return_value=mock_image)
        MockGetTTS.return_value.synthesize = AsyncMock(return_value=mock_tts)

        # Create a GenerationRequest object
        request = GenerationRequest(
            child_name="小明",
            age_months=24,
            theme_topic="刷牙",
            theme_category="habit",
            art_style="watercolor",
            protagonist=ProtagonistConfig(
                animal="bear",
                color="brown",
                accessory="red scarf",
            ),
        )

        pipeline = PictureBookPipeline()
        result = await pipeline.generate(request=request)

        assert result["title"] == "小明学刷牙"
        assert len(result["pages"]) == 1
        assert result["style_config"]["art_style"] == "watercolor"
        assert result["style_config"]["protagonist_animal"] == "bear"
