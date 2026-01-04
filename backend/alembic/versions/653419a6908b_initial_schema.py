"""initial_schema

Revision ID: 653419a6908b
Revises:
Create Date: 2025-12-08 11:54:42.200002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653419a6908b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('openid', sa.String(64), nullable=False, unique=True, index=True),
        sa.Column('unionid', sa.String(64), nullable=True, unique=True),
        sa.Column('nickname', sa.String(100), nullable=False, default=''),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Children table
    op.create_table(
        'children',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('birth_date', sa.Date, nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('favorite_characters', sa.JSON, nullable=False, default=list),
        sa.Column('interests', sa.JSON, nullable=False, default=list),
        sa.Column('current_stage', sa.String(50), nullable=True),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Child settings table
    op.create_table(
        'child_settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('child_id', sa.String(36), sa.ForeignKey('children.id'), nullable=False, unique=True),
        sa.Column('daily_limit_minutes', sa.Integer, nullable=False, default=30),
        sa.Column('content_preferences', sa.JSON, nullable=False, default=dict),
        sa.Column('notification_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('auto_play', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Contents table
    op.create_table(
        'contents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('child_id', sa.String(36), sa.ForeignKey('children.id'), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content_type', sa.Enum('picture_book', 'nursery_rhyme', 'video', name='contenttype'), nullable=False),
        sa.Column('theme_category', sa.Enum('habit', 'cognition', name='themecategory'), nullable=False),
        sa.Column('theme_topic', sa.String(100), nullable=False),
        sa.Column('personalization', sa.JSON, nullable=False, default=dict),
        sa.Column('content_data', sa.JSON, nullable=False, default=dict),
        sa.Column('status', sa.Enum('pending', 'generating', 'ready', 'failed', name='contentstatus'), nullable=False, default='pending'),
        sa.Column('review_status', sa.Enum('pending', 'approved', 'rejected', 'manual_review', name='reviewstatus'), nullable=False, default='pending'),
        sa.Column('review_result', sa.JSON, nullable=False, default=dict),
        sa.Column('generated_by', sa.JSON, nullable=False, default=dict),
        sa.Column('duration', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Content assets table
    op.create_table(
        'content_assets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False),
        sa.Column('asset_type', sa.Enum('text', 'image', 'audio', 'video', name='assettype'), nullable=False),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=False, default=0),
        sa.Column('duration', sa.Integer, nullable=True),
        sa.Column('metadata', sa.JSON, nullable=False, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Play history table
    op.create_table(
        'play_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('child_id', sa.String(36), sa.ForeignKey('children.id'), nullable=False, index=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False, index=True),
        sa.Column('duration', sa.Integer, nullable=False, default=0),
        sa.Column('completed', sa.Boolean, nullable=False, default=False),
        sa.Column('progress', sa.Float, nullable=False, default=0.0),
        sa.Column('interactions', sa.JSON, nullable=False, default=list),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Favorites table
    op.create_table(
        'favorites',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'content_id', name='uq_user_content_favorite'),
    )

    # Shares table
    op.create_table(
        'shares',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False, index=True),
        sa.Column('platform', sa.Enum('wechat', 'wechat_moments', 'qr_code', 'link', name='shareplatform'), nullable=False),
        sa.Column('share_code', sa.String(32), nullable=False, unique=True, index=True),
        sa.Column('view_count', sa.Integer, nullable=False, default=0),
        sa.Column('poster_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('shares')
    op.drop_table('favorites')
    op.drop_table('play_history')
    op.drop_table('content_assets')
    op.drop_table('contents')
    op.drop_table('child_settings')
    op.drop_table('children')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS shareplatform')
    op.execute('DROP TYPE IF EXISTS reviewstatus')
    op.execute('DROP TYPE IF EXISTS contentstatus')
    op.execute('DROP TYPE IF EXISTS assettype')
    op.execute('DROP TYPE IF EXISTS themecategory')
    op.execute('DROP TYPE IF EXISTS contenttype')
