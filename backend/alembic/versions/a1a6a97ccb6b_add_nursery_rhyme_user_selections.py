"""add_nursery_rhyme_user_selections

Revision ID: a1a6a97ccb6b
Revises: 653419a6908b
Create Date: 2025-12-20 21:41:21.139057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'a1a6a97ccb6b'
down_revision: Union[str, Sequence[str], None] = '653419a6908b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new columns to contents table for nursery rhyme redesign."""
    op.add_column('contents', sa.Column('user_selections', JSONB, nullable=True))
    op.add_column('contents', sa.Column('user_prompt', sa.Text(), nullable=True))
    op.add_column('contents', sa.Column('enhanced_prompt', sa.Text(), nullable=True))
    op.add_column('contents', sa.Column('all_tracks', JSONB, nullable=True))


def downgrade() -> None:
    """Remove nursery rhyme redesign columns."""
    op.drop_column('contents', 'all_tracks')
    op.drop_column('contents', 'enhanced_prompt')
    op.drop_column('contents', 'user_prompt')
    op.drop_column('contents', 'user_selections')
