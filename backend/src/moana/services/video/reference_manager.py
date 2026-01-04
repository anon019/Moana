"""Reference image manager for Veo 3.1 character consistency."""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CharacterReference:
    """A character's reference image collection."""
    character_id: str
    image_urls: list[str]
    description: str = ""


class ReferenceImageManager:
    """Manages reference images for character consistency in Veo 3.1.

    Veo 3.1 supports up to 3 reference images per generation to maintain
    visual consistency of characters, products, or styles.
    """

    MAX_REFERENCE_IMAGES = 3

    def __init__(self):
        self._character_cache: dict[str, CharacterReference] = {}

    def register_character(
        self,
        character_id: str,
        image_urls: list[str],
        description: str = "",
    ) -> None:
        """Register a character with reference images.

        Args:
            character_id: Unique identifier for the character
            image_urls: List of image URLs (different angles/expressions)
            description: Text description of the character
        """
        # Keep only up to MAX references
        selected = image_urls[:self.MAX_REFERENCE_IMAGES]

        self._character_cache[character_id] = CharacterReference(
            character_id=character_id,
            image_urls=selected,
            description=description,
        )
        logger.info(f"Registered character '{character_id}' with {len(selected)} reference images")

    def get_references_for_scene(
        self,
        character_ids: list[str],
    ) -> list[str]:
        """Get reference images for characters in a scene.

        Distributes the 3-image limit among requested characters:
        - 1 character: 3 refs
        - 2 characters: 2 + 1 refs (first is primary)
        - 3+ characters: 1 each (up to 3)

        Args:
            character_ids: List of character IDs in the scene

        Returns:
            List of reference image URLs (max 3)
        """
        if not character_ids:
            return []

        # Filter to known characters
        known_chars = [
            cid for cid in character_ids
            if cid in self._character_cache
        ]

        if not known_chars:
            return []

        all_refs: list[str] = []
        num_chars = len(known_chars)

        # Calculate refs per character
        if num_chars == 1:
            refs_per_char = [3]
        elif num_chars == 2:
            refs_per_char = [2, 1]  # Primary character gets more
        else:
            refs_per_char = [1] * min(num_chars, 3)

        # Collect refs from each character
        for i, char_id in enumerate(known_chars[:3]):
            char_data = self._character_cache[char_id]
            quota = refs_per_char[i] if i < len(refs_per_char) else 0
            all_refs.extend(char_data.image_urls[:quota])

        return all_refs[:self.MAX_REFERENCE_IMAGES]

    def get_character_description(self, character_id: str) -> str:
        """Get a character's description for prompt enhancement.

        Args:
            character_id: The character ID

        Returns:
            Description string, or empty string if not found
        """
        if character_id in self._character_cache:
            return self._character_cache[character_id].description
        return ""

    def clear_character(self, character_id: str) -> None:
        """Remove a character from the cache.

        Args:
            character_id: The character ID to remove
        """
        if character_id in self._character_cache:
            del self._character_cache[character_id]
            logger.info(f"Cleared character '{character_id}'")

    def clear_all(self) -> None:
        """Clear all registered characters."""
        self._character_cache.clear()
        logger.info("Cleared all character references")

    def list_characters(self) -> list[dict]:
        """List all registered characters.

        Returns:
            List of character info dicts
        """
        return [
            {
                "id": char_id,
                "description": char.description,
                "image_count": len(char.image_urls),
            }
            for char_id, char in self._character_cache.items()
        ]
