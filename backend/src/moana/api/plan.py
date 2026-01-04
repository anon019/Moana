"""Plan API - 学习计划相关端点."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from moana.agents.planner import PlannerAgent
from moana.agents.schemas import DayPlan, WeeklyPlan
from moana.pipelines.picture_book import PictureBookPipeline
from moana.pipelines.nursery_rhyme import NurseryRhymePipeline
from moana.services.music.base import MusicStyle


router = APIRouter()


class WeeklyPlanRequest(BaseModel):
    """Request to generate weekly plan."""
    child_id: str = Field(description="Child ID")
    child_name: str = Field(description="Child name")
    age_months: int = Field(ge=12, le=72, description="Child age in months")
    preferences: list[str] = Field(default=[], description="Preferred themes/characters")


class GenerateDayRequest(BaseModel):
    """Request to generate content for a day."""
    day_plan: DayPlan = Field(description="Day plan from weekly plan")
    child_name: str = Field(description="Child name")
    age_months: int = Field(ge=12, le=72, description="Child age in months")
    content_type: str = Field(
        pattern="^(picture_book|nursery_rhyme|video)$",
        description="Content type to generate"
    )


@router.post("/weekly", response_model=WeeklyPlan)
async def generate_weekly_plan(request: WeeklyPlanRequest):
    """Generate a weekly learning plan for a child.

    根据孩子信息生成个性化的一周学习计划。
    计划包含每天的主题、内容形式和创作提示。
    """
    agent = PlannerAgent()

    try:
        # TODO: 从数据库查询已学主题
        learned_themes: list[str] = []

        result = await agent.generate_weekly_plan(
            child_id=request.child_id,
            child_name=request.child_name,
            age_months=request.age_months,
            preferences=request.preferences,
            learned_themes=learned_themes,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-day")
async def generate_day_content(request: GenerateDayRequest):
    """Generate content for a specific day from the plan.

    根据计划中的某一天生成具体内容。
    """
    day = request.day_plan
    content_type = request.content_type

    try:
        if content_type == "picture_book":
            pipeline = PictureBookPipeline()
            result = await pipeline.generate(
                child_name=request.child_name,
                age_months=request.age_months,
                theme_topic=day.theme,
                theme_category=day.category,
            )
        elif content_type == "nursery_rhyme":
            pipeline = NurseryRhymePipeline()
            result = await pipeline.generate(
                child_name=request.child_name,
                age_months=request.age_months,
                theme_topic=day.theme,
                theme_category=day.category,
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
