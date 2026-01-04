# tests/models/test_content.py
import pytest


def test_content_model_creation():
    """Test Content model can be instantiated."""
    from moana.models.content import Content, ContentType, ThemeCategory

    content = Content(
        title="小莫学刷牙",
        content_type=ContentType.PICTURE_BOOK,
        theme_category=ThemeCategory.HABIT,
        theme_topic="刷牙",
        personalization={"child_name": "小莫"},
    )

    assert content.title == "小莫学刷牙"
    assert content.content_type == ContentType.PICTURE_BOOK
    assert content.theme_category == ThemeCategory.HABIT


def test_content_asset_model():
    """Test ContentAsset model."""
    from moana.models.content import ContentAsset, AssetType

    asset = ContentAsset(
        asset_type=AssetType.IMAGE,
        url="https://example.com/image.png",
        asset_metadata={"prompt": "A cute girl brushing teeth"},
    )

    assert asset.asset_type == AssetType.IMAGE
    assert "prompt" in asset.asset_metadata
