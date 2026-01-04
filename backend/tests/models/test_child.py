import pytest
from datetime import date


def test_child_model_creation():
    """Test Child model can be instantiated."""
    from moana.models.child import Child

    child = Child(
        name="小莫",
        birth_date=date(2024, 2, 5),
        favorite_characters=["小兔子", "小狐狸"],
        interests=["动物", "唱歌"],
    )

    assert child.name == "小莫"
    assert child.birth_date == date(2024, 2, 5)
    assert "小兔子" in child.favorite_characters


def test_child_age_in_months():
    """Test age calculation in months."""
    from moana.models.child import Child
    from datetime import date

    # Mock today as 2025-12-05
    child = Child(
        name="小莫",
        birth_date=date(2024, 2, 5),
    )

    # 22 months old
    age = child.age_in_months(reference_date=date(2025, 12, 5))
    assert age == 22
