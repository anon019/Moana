"""Intent API - 意图理解相关端点."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from moana.agents.intent import IntentAgent
from moana.agents.schemas import ParsedIntent
from moana.pipelines.picture_book import PictureBookPipeline
from moana.pipelines.nursery_rhyme import NurseryRhymePipeline
from moana.services.music.base import MusicStyle


router = APIRouter()


class IntentParseRequest(BaseModel):
    """Request to parse parent intent."""
    child_name: str = Field(description="Child name")
    age_months: int = Field(ge=12, le=72, description="Child age in months")
    user_input: str = Field(description="Parent's natural language input")
    preferred_types: list[str] | None = Field(
        default=None,
        description="Preferred content types"
    )


class IntentGenerateRequest(BaseModel):
    """Request to generate content from parsed intent."""
    parsed_intent: ParsedIntent = Field(description="Parsed intent")
    child_name: str = Field(description="Child name")
    age_months: int = Field(ge=12, le=72, description="Child age in months")
    content_type: str = Field(
        pattern="^(picture_book|nursery_rhyme|video)$",
        description="Content type to generate"
    )


@router.post("/parse", response_model=ParsedIntent)
async def parse_intent(request: IntentParseRequest):
    """Parse parent's natural language input.

    理解家长输入，提取主题并生成创作提示。
    支持的输入类型：IP/影视、生活事件、兴趣关键词、行为引导。
    """
    agent = IntentAgent()

    try:
        result = await agent.parse(
            child_name=request.child_name,
            age_months=request.age_months,
            user_input=request.user_input,
            preferred_types=request.preferred_types,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_from_intent(request: IntentGenerateRequest):
    """Generate content based on parsed intent.

    根据解析后的意图生成具体内容。
    """
    intent = request.parsed_intent
    content_type = request.content_type

    try:
        if content_type == "picture_book":
            pipeline = PictureBookPipeline()
            result = await pipeline.generate(
                child_name=request.child_name,
                age_months=request.age_months,
                theme_topic=intent.theme,
                theme_category=intent.category,
            )
        elif content_type == "nursery_rhyme":
            pipeline = NurseryRhymePipeline()
            result = await pipeline.generate(
                child_name=request.child_name,
                age_months=request.age_months,
                theme_topic=intent.theme,
                theme_category=intent.category,
                music_style=MusicStyle.CHEERFUL,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content type: {content_type}"
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
