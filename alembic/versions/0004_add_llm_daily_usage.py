"""Add daily LLM usage table and remove goal user default.

Revision ID: 0004_add_llm_daily_usage
Revises: 0003_add_indexes_to_quest_log
Create Date: 2025-10-19
"""

from __future__ import annotations

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision = "0004_add_llm_daily_usage"
down_revision = "0003_add_indexes_to_quest_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_daily_usage",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    with op.batch_alter_table("goals") as batch:
        batch.alter_column("user_id", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("goals") as batch:
        batch.alter_column("user_id", server_default="default_user")

    op.drop_table("llm_daily_usage")
