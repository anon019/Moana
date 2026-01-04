"""Tests for reference image manager."""
import pytest
from moana.services.video.reference_manager import ReferenceImageManager


class TestReferenceImageManager:
    """Test reference image management."""

    @pytest.fixture
    def manager(self):
        """Create manager instance."""
        return ReferenceImageManager()

    def test_register_character(self, manager):
        """Should register a character with images."""
        manager.register_character(
            character_id="bunny",
            image_urls=["img1.png", "img2.png"],
            description="white rabbit",
        )
        assert "bunny" in manager._character_cache

    def test_get_references_single_character(self, manager):
        """Should return all refs for single character."""
        manager.register_character(
            character_id="bunny",
            image_urls=["img1.png", "img2.png", "img3.png"],
        )
        refs = manager.get_references_for_scene(["bunny"])
        assert len(refs) == 3

    def test_get_references_max_limit(self, manager):
        """Should limit to 3 reference images total."""
        manager.register_character(
            character_id="bunny",
            image_urls=["b1.png", "b2.png", "b3.png", "b4.png", "b5.png"],
        )
        refs = manager.get_references_for_scene(["bunny"])
        assert len(refs) <= 3

    def test_get_references_multiple_characters(self, manager):
        """Should distribute refs among multiple characters."""
        manager.register_character("bunny", ["b1.png", "b2.png", "b3.png"])
        manager.register_character("fox", ["f1.png", "f2.png", "f3.png"])

        refs = manager.get_references_for_scene(["bunny", "fox"])
        assert len(refs) <= 3
        # Should have refs from both characters
        assert any("b" in r for r in refs)
        assert any("f" in r for r in refs)

    def test_get_references_unknown_character(self, manager):
        """Should handle unknown character gracefully."""
        refs = manager.get_references_for_scene(["unknown"])
        assert refs == []

    def test_clear_character(self, manager):
        """Should clear a character's references."""
        manager.register_character("bunny", ["img1.png"])
        manager.clear_character("bunny")
        assert "bunny" not in manager._character_cache

    def test_clear_all(self, manager):
        """Should clear all character references."""
        manager.register_character("bunny", ["img1.png"])
        manager.register_character("fox", ["img2.png"])
        manager.clear_all()
        assert len(manager._character_cache) == 0

    def test_list_characters(self, manager):
        """Should list all registered characters."""
        manager.register_character("bunny", ["img1.png", "img2.png"], "white rabbit")
        manager.register_character("fox", ["img3.png"], "red fox")

        chars = manager.list_characters()
        assert len(chars) == 2
        assert any(c["id"] == "bunny" for c in chars)
        assert any(c["id"] == "fox" for c in chars)

    def test_get_character_description(self, manager):
        """Should get character description."""
        manager.register_character("bunny", ["img1.png"], "white rabbit")
        desc = manager.get_character_description("bunny")
        assert desc == "white rabbit"

    def test_get_character_description_unknown(self, manager):
        """Should return empty string for unknown character."""
        desc = manager.get_character_description("unknown")
        assert desc == ""
