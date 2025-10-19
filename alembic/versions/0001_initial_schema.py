"""Initial database schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-10-18
"""

from __future__ import annotations

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("goal_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, server_default="default_user"),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("goal_type", sa.String(), nullable=False, server_default="ONE_TIME"),
        sa.Column("motivation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "boss_stages",
        sa.Column("boss_id", sa.String(), primary_key=True),
        sa.Column(
            "goal_id",
            sa.String(),
            sa.ForeignKey("goals.goal_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("success_criteria", sa.Text(), nullable=True),
        sa.Column("stage_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="PLANNED"),
        sa.Column("target_week", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "quests",
        sa.Column("quest_id", sa.String(), primary_key=True),
        sa.Column(
            "goal_id",
            sa.String(),
            sa.ForeignKey("goals.goal_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty_tier", sa.String(), nullable=False, server_default="NORMAL"),
        sa.Column("expected_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("variation_tags", sa.Text(), nullable=True),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("origin_prompt_hash", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "quest_logs",
        sa.Column("log_id", sa.String(), primary_key=True),
        sa.Column(
            "quest_id",
            sa.String(),
            sa.ForeignKey("quests.quest_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "goal_id",
            sa.String(),
            sa.ForeignKey("goals.goal_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.String(), nullable=False),
        sa.Column("perceived_difficulty", sa.String(), nullable=True),
        sa.Column("energy_status", sa.String(), nullable=True),
        sa.Column("loot_type", sa.String(), nullable=True),
        sa.Column("mood_note", sa.Text(), nullable=True),
        sa.Column("llm_variation_seed", sa.String(), nullable=True),
    )

    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("challenge_appetite", sa.String(), nullable=False, server_default="MEDIUM"),
        sa.Column("theme_preference", sa.String(), nullable=False, server_default="GAME"),
        sa.Column(
            "onboarding_stage",
            sa.String(),
            nullable=False,
            server_default="STAGE_0_ONBOARDING",
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "player_progress",
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("focus_goal_id", sa.String(), nullable=True),
        sa.Column(
            "stage_label",
            sa.String(),
            nullable=False,
            server_default="STAGE_0_ONBOARDING",
        ),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("experience_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak_weeks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_reflection_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "reminders",
        sa.Column("reminder_id", sa.String(), primary_key=True),
        sa.Column(
            "goal_id",
            sa.String(),
            sa.ForeignKey("goals.goal_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(), nullable=False, server_default="slack"),
        sa.Column("frequency", sa.String(), nullable=False, server_default="daily"),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferred_time", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )


def downgrade() -> None:
    op.drop_table("reminders")
    op.drop_table("player_progress")
    op.drop_table("user_preferences")
    op.drop_table("quest_logs")
    op.drop_table("quests")
    op.drop_table("boss_stages")
    op.drop_table("goals")
