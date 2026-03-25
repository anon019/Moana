"""add_play_history_tables

Revision ID: d3e4f5a6b7c8
Revises: a1a6a97ccb6b
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "a1a6a97ccb6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names(bind) -> set[str]:
    return set(sa.inspect(bind).get_table_names())


def _index_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    """Create play tracking tables and migrate legacy data if present."""
    bind = op.get_bind()
    existing_tables = _table_names(bind)

    if "play_histories" not in existing_tables:
        op.create_table(
            "play_histories",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
            sa.Column("content_id", sa.String(36), sa.ForeignKey("contents.id"), nullable=False),
            sa.Column("content_type", sa.String(50), nullable=False),
            sa.Column("current_page", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("total_pages", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("completion_rate", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("last_played_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if "interaction_records" not in existing_tables:
        op.create_table(
            "interaction_records",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("play_history_id", sa.String(36), sa.ForeignKey("play_histories.id"), nullable=False),
            sa.Column("page_num", sa.Integer(), nullable=False),
            sa.Column("question_type", sa.String(50), nullable=False),
            sa.Column("is_correct", sa.Boolean(), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("time_spent_ms", sa.Integer(), nullable=False),
            sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    play_index_names = _index_names(bind, "play_histories")
    for index_name, columns in [
        ("ix_play_histories_child_started_at", ["child_id", "started_at"]),
        ("ix_play_histories_child_last_played_at", ["child_id", "last_played_at"]),
        ("ix_play_histories_child_content_type", ["child_id", "content_type"]),
        ("ix_play_histories_child_content_completed_last_played", ["child_id", "content_id", "completed_at", "last_played_at"]),
    ]:
        if index_name not in play_index_names:
            op.create_index(index_name, "play_histories", columns, unique=False)

    interaction_index_names = _index_names(bind, "interaction_records")
    for index_name, columns in [
        ("ix_interaction_records_play_history_question_type", ["play_history_id", "question_type"]),
        ("ix_interaction_records_play_history_is_correct", ["play_history_id", "is_correct"]),
    ]:
        if index_name not in interaction_index_names:
            op.create_index(index_name, "interaction_records", columns, unique=False)

    existing_tables = _table_names(bind)
    if "play_history" in existing_tables and "play_histories" in existing_tables:
        op.execute(sa.text("""
            INSERT INTO play_histories (
                id,
                child_id,
                content_id,
                content_type,
                current_page,
                total_pages,
                completion_rate,
                started_at,
                last_played_at,
                completed_at,
                created_at,
                updated_at
            )
            SELECT
                legacy.id,
                legacy.child_id,
                legacy.content_id,
                COALESCE(CAST(contents.content_type AS TEXT), 'picture_book') AS content_type,
                1 AS current_page,
                1 AS total_pages,
                CASE
                    WHEN COALESCE(legacy.completed, FALSE) THEN 1.0
                    ELSE GREATEST(LEAST(COALESCE(legacy.progress, 0.0), 1.0), 0.0)
                END AS completion_rate,
                legacy.created_at AS started_at,
                COALESCE(legacy.updated_at, legacy.created_at) AS last_played_at,
                CASE
                    WHEN COALESCE(legacy.completed, FALSE)
                    THEN COALESCE(legacy.updated_at, legacy.created_at)
                    ELSE NULL
                END AS completed_at,
                legacy.created_at,
                COALESCE(legacy.updated_at, legacy.created_at)
            FROM play_history AS legacy
            LEFT JOIN contents ON contents.id = legacy.content_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM play_histories AS current
                WHERE current.id = legacy.id
            )
        """))


def downgrade() -> None:
    """Drop play tracking tables created by this migration."""
    bind = op.get_bind()
    existing_tables = _table_names(bind)

    if "interaction_records" in existing_tables:
        op.drop_table("interaction_records")

    if "play_histories" in existing_tables:
        op.drop_table("play_histories")
