"""Tests for SmartPromptAnalyzer."""
import pytest
from unittest.mock import patch, MagicMock
from moana.services.smart import SmartPromptAnalyzer, AnalysisResult


class TestSmartPromptAnalyzer:
    """Test SmartPromptAnalyzer service."""

    @pytest.fixture
    def analyzer(self):
        return SmartPromptAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_habit_prompt(self, analyzer):
        """Test analyzing a habit-related prompt."""
        result = await analyzer.analyze(
            custom_prompt="宝宝最近不爱吃蔬菜，总是把胡萝卜挑出来",
            child_name="小明",
            age_months=36,
            content_type="picture_book",
        )

        assert isinstance(result, AnalysisResult)
        assert result.theme_topic  # Should have a topic
        assert result.enhanced_prompt  # Should have enhanced prompt
        assert "小明" in result.title  # Title should contain child name

    @pytest.mark.asyncio
    async def test_analyze_returns_fallback_on_error(self):
        """Test that analyzer returns fallback on LLM error."""
        # Mock the genai client to raise an error
        with patch("moana.services.smart.prompt_analyzer.genai.Client") as MockClient:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = Exception("API Error")
            MockClient.return_value = mock_client

            analyzer = SmartPromptAnalyzer()
            result = await analyzer.analyze(
                custom_prompt="测试内容",
                child_name="测试宝贝",
                age_months=24,
                content_type="video",
            )

            assert isinstance(result, AnalysisResult)
            assert result.theme_category == "cognition"  # Default fallback
            assert result.title == "测试宝贝的故事"  # Default title with child name
