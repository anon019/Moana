"""add_task_status_and_child_settings_fields

Revision ID: e5f6a7b8c9d0
Revises: d3e4f5a6b7c8
Create Date: 2026-03-25 13:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names(bind) -> set[str]:
    return set(sa.inspect(bind).get_table_names())


def _column_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    """Add persisted task status support and child settings fields."""
    bind = op.get_bind()
    tables = _table_names(bind)

    if "task_statuses" not in tables:
        op.create_table(
            "task_statuses",
            sa.Column("task_id", sa.String(128), primary_key=True),
            sa.Column("task_type", sa.String(64), nullable=False, server_default=sa.text("generic")),
            sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("pending")),
            sa.Column("progress", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("stage", sa.String(64), nullable=True),
            sa.Column("message", sa.String(512), nullable=True),
            sa.Column("error", sa.String(1024), nullable=True),
            sa.Column("content_id", sa.String(36), nullable=True),
            sa.Column("result", sa.JSON(), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    task_status_indexes = _index_names(bind, "task_statuses")
    for index_name, columns in [
        ("ix_task_statuses_task_type", ["task_type"]),
        ("ix_task_statuses_status", ["status"]),
        ("ix_task_statuses_content_id", ["content_id"]),
        ("ix_task_statuses_finished_at", ["finished_at"]),
    ]:
        if index_name not in task_status_indexes:
            op.create_index(index_name, "task_statuses", columns, unique=False)

    if "child_settings" in tables:
        child_columns = _column_names(bind, "child_settings")

        if "session_limit_minutes" not in child_columns:
            op.add_column(
                "child_settings",
                sa.Column("session_limit_minutes", sa.Integer(), nullable=False, server_default=sa.text("20")),
            )

        if "rest_reminder_enabled" not in child_columns:
            op.add_column(
                "child_settings",
                sa.Column("rest_reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            )

        child_columns = _column_names(bind, "child_settings")
        if "notification_enabled" in child_columns and "rest_reminder_enabled" in child_columns:
            op.execute(
                sa.text(
                    "UPDATE child_settings SET rest_reminder_enabled = notification_enabled"
                )
            )


def downgrade() -> None:
    """Revert task status support and child settings additions."""
    bind = op.get_bind()
    tables = _table_names(bind)

    if "child_settings" in tables:
        child_columns = _column_names(bind, "child_settings")
        if "rest_reminder_enabled" in child_columns:
            op.drop_column("child_settings", "rest_reminder_enabled")
        if "session_limit_minutes" in child_columns:
            op.drop_column("child_settings", "session_limit_minutes")

    if "task_statuses" in tables:
        for index_name in [
            "ix_task_statuses_finished_at",
            "ix_task_statuses_content_id",
            "ix_task_statuses_status",
            "ix_task_statuses_task_type",
        ]:
            if index_name in _index_names(bind, "task_statuses"):
                op.drop_index(index_name, table_name="task_statuses")
        op.drop_table("task_statuses")
