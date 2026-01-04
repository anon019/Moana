import pytest


def test_lyric_section_model():
    """Test LyricSection model."""
    from moana.agents.schemas import LyricSection

    section = LyricSection(
        tag="verse",
        content="小莫早起床，揉揉小眼睛",
        order=1,
    )

    assert section.tag == "verse"
    assert section.order == 1


def test_nursery_rhyme_lyrics_model():
    """Test NurseryRhymeLyrics model."""
    from moana.agents.schemas import NurseryRhymeLyrics, LyricSection

    lyrics = NurseryRhymeLyrics(
        title="小莫刷牙歌",
        theme_topic="刷牙",
        lyrics_text="[Verse]\n小莫早起床\n[Chorus]\n刷刷刷",
        sections=[
            LyricSection(tag="verse", content="小莫早起床", order=1),
            LyricSection(tag="chorus", content="刷刷刷", order=2),
        ],
        style_prompt="cheerful children song, cute voice",
        cover_prompt="A cute girl brushing teeth happily",
        educational_goal="养成早晚刷牙的好习惯",
    )

    assert lyrics.title == "小莫刷牙歌"
    assert len(lyrics.sections) == 2
    assert lyrics.sections[0].tag == "verse"


def test_day_plan_schema():
    """Test DayPlan schema."""
    from moana.agents.schemas import DayPlan

    plan = DayPlan(
        day=1,
        date="2025-12-09",
        theme="刷牙",
        category="habit",
        content_types=["picture_book", "nursery_rhyme"],
        story_hint="小动物学刷牙",
        song_hint="欢快的刷牙歌",
    )
    assert plan.day == 1
    assert plan.category == "habit"


def test_weekly_plan_schema():
    """Test WeeklyPlan schema."""
    from moana.agents.schemas import WeeklyPlan, DayPlan

    days = [
        DayPlan(
            day=1,
            date="2025-12-09",
            theme="刷牙",
            category="habit",
            content_types=["picture_book"],
            story_hint="test",
            song_hint=None,
        )
    ]
    plan = WeeklyPlan(
        week_start="2025-12-09",
        child_id="child_001",
        child_name="小莫",
        age_months=24,
        days=days,
    )
    assert plan.child_name == "小莫"
    assert len(plan.days) == 1


def test_parsed_intent_schema():
    """Test ParsedIntent schema."""
    from moana.agents.schemas import ParsedIntent

    intent = ParsedIntent(
        intent_type="life_event",
        original_input="明天要打疫苗",
        theme="打疫苗",
        category="habit",
        educational_goal="缓解打疫苗恐惧",
        story_prompt="小动物打疫苗的故事",
        song_prompt="勇敢歌",
        video_prompt=None,
        recommended_types=["picture_book", "nursery_rhyme"],
    )
    assert intent.intent_type == "life_event"
    assert intent.theme == "打疫苗"
