"""Add indexes to quest log foreign keys.

Revision ID: 0003_add_indexes_to_quest_log
Revises: 0002_add_llm_usage_ledger
Create Date: 2025-10-19
"""

from __future__ import annotations

from alembic import op  # type: ignore[attr-defined]


revision = "0003_add_indexes_to_quest_log"
down_revision = "0002_add_llm_usage_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_quest_logs_goal_id", "quest_logs", ["goal_id"])
    op.create_index("ix_quest_logs_quest_id", "quest_logs", ["quest_id"])


def downgrade() -> None:
    op.drop_index("ix_quest_logs_quest_id", table_name="quest_logs")
    op.drop_index("ix_quest_logs_goal_id", table_name="quest_logs")
