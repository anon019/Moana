# tests/test_integration.py
"""Integration tests for Phase 6 features."""
import pytest


class TestPhase6Integration:
    """Integration tests for Phase 6 backend features."""

    def test_all_models_import(self):
        """Test all models can be imported."""
        from moana.models import (
            Base,
            User,
            Child,
            Content,
            ContentAsset,
            PlayHistory,
            ChildSettings,
            Favorite,
            Share,
            SharePlatform,
            ContentType,
            ReviewStatus,
        )
        assert all([
            Base, User, Child, Content, ContentAsset,
            PlayHistory, ChildSettings, Favorite, Share,
            SharePlatform, ContentType, ReviewStatus,
        ])

    def test_all_agents_import(self):
        """Test all agents can be imported."""
        from moana.agents import (
            StoryAgent,
            SongAgent,
            PlannerAgent,
            IntentAgent,
            ReviewAgent,
            AnalyticsAgent,
        )
        assert all([
            StoryAgent, SongAgent, PlannerAgent,
            IntentAgent, ReviewAgent, AnalyticsAgent,
        ])

    def test_all_services_import(self):
        """Test all services can be imported."""
        from moana.services.wechat import WeChatService
        from moana.services.moderation import (
            ModerationService,
            AliyunModerationService,
        )
        from moana.services.storage import (
            StorageService,
            OSSStorageService,
        )
        from moana.services.analytics import AnalyticsStatsService
        from moana.services.share import ShareService, PosterService

        assert all([
            WeChatService, ModerationService, AliyunModerationService,
            StorageService, OSSStorageService, AnalyticsStatsService,
            ShareService, PosterService,
        ])

    def test_all_routers_import(self):
        """Test all routers can be imported."""
        from moana.routers import (
            auth_router,
            analytics_router,
            library_router,
        )
        assert all([auth_router, analytics_router, library_router])

    def test_all_schemas_import(self):
        """Test all schemas can be imported."""
        from moana.schemas import (
            WeChatLoginRequest,
            TokenResponse,
            RefreshTokenRequest,
            UserResponse,
        )
        assert all([
            WeChatLoginRequest, TokenResponse,
            RefreshTokenRequest, UserResponse,
        ])

    def test_security_utils_import(self):
        """Test security utilities can be imported."""
        from moana.utils.security import (
            create_access_token,
            create_refresh_token,
            decode_access_token,
        )
        assert all([
            create_access_token,
            create_refresh_token,
            decode_access_token,
        ])

    def test_database_import(self):
        """Test database utilities can be imported."""
        from moana.database import (
            get_db,
            get_engine,
            init_db,
        )
        assert all([get_db, get_engine, init_db])

    def test_config_import(self):
        """Test config can be imported."""
        from moana.config import get_settings

        settings = get_settings()
        assert settings.jwt_secret_key is not None
        assert settings.jwt_algorithm == "HS256"
        assert settings.wechat_app_id is not None


class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_token_roundtrip(self):
        """Test token creation and decoding."""
        from moana.utils.security import (
            create_access_token,
            decode_access_token,
        )

        # Create token
        token = create_access_token(data={"sub": "user123", "role": "parent"})
        assert token is not None

        # Decode token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "parent"
        assert payload["type"] == "access"

    def test_refresh_token_type(self):
        """Test refresh token has correct type."""
        from moana.utils.security import (
            create_refresh_token,
            decode_access_token,
        )

        token = create_refresh_token(data={"sub": "user123"})
        payload = decode_access_token(token)

        assert payload["type"] == "refresh"


class TestModerationIntegration:
    """Integration tests for moderation features."""

    @pytest.mark.asyncio
    async def test_moderation_flow(self):
        """Test moderation service flow."""
        from moana.services.moderation import AliyunModerationService

        service = AliyunModerationService()

        # Test text moderation
        result = await service.moderate_text("这是一个测试内容")
        assert result.is_safe is True

        # Test image moderation
        result = await service.moderate_image("https://example.com/test.png")
        assert result.is_safe is True


class TestAnalyticsIntegration:
    """Integration tests for analytics features."""

    def test_child_stats_creation(self):
        """Test ChildStats can be created."""
        from moana.services.analytics import ChildStats
        from moana.models import ContentType

        stats = ChildStats(
            child_id="child123",
            total_plays=100,
            total_duration=3600,
            favorite_content_type=ContentType.NURSERY_RHYME,
            streak_days=7,
        )

        assert stats.total_plays == 100
        assert stats.streak_days == 7

        stats_dict = stats.to_dict()
        assert stats_dict["favorite_content_type"] == "nursery_rhyme"


class TestShareIntegration:
    """Integration tests for share features."""

    def test_share_model_generation(self):
        """Test Share model generates share code."""
        from moana.models import Share, SharePlatform

        share = Share(
            user_id="user123",
            content_id="content456",
            platform=SharePlatform.WECHAT,
        )

        assert share.share_code is not None
        assert len(share.share_code) > 0
        assert share.view_count == 0

    @pytest.mark.asyncio
    async def test_poster_generation(self):
        """Test poster can be generated."""
        from moana.services.share import PosterService

        service = PosterService()
        result = await service.generate_poster(
            title="测试绘本",
            subtitle="习惯养成",
            qr_data="https://example.com/share/abc123",
        )

        # Should succeed if Pillow is installed
        assert result is not None
        if result.success:
            assert result.image_bytes is not None
            assert len(result.image_bytes) > 0
