"""SQLAlchemy models for Goaler."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class Goal(Base):
    __tablename__ = "goals"

    goal_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    goal_type: Mapped[str] = mapped_column(String, default="ONE_TIME")
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String, default="IN_PROGRESS")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    boss_stages: Mapped[list["BossStage"]] = relationship(
        "BossStage", cascade="all, delete-orphan", back_populates="goal"
    )
    quests: Mapped[list["Quest"]] = relationship(
        "Quest", cascade="all, delete-orphan", back_populates="goal"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", cascade="all, delete-orphan", back_populates="goal"
    )
    metrics: Mapped[list["Metric"]] = relationship(
        "Metric", cascade="all, delete-orphan", back_populates="goal"
    )
    quest_logs: Mapped[list["QuestLog"]] = relationship(
        "QuestLog", cascade="all, delete-orphan", back_populates="goal"
    )
    conversation_logs: Mapped[list["ConversationLog"]] = relationship(
        "ConversationLog", cascade="all, delete-orphan", back_populates="goal"
    )


class BossStage(Base):
    __tablename__ = "boss_stages"

    boss_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    success_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="PLANNED")
    target_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped[Goal] = relationship("Goal", back_populates="boss_stages")


class Quest(Base):
    __tablename__ = "quests"

    quest_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_tier: Mapped[str] = mapped_column(String, default="NORMAL")
    expected_duration_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    variation_tags: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # comma separated tags
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    origin_prompt_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=func.now()
    )

    goal: Mapped[Goal] = relationship("Goal", back_populates="quests")
    logs: Mapped[list["QuestLog"]] = relationship(
        "QuestLog", cascade="all, delete-orphan", back_populates="quest"
    )


class QuestLog(Base):
    __tablename__ = "quest_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    quest_id: Mapped[str] = mapped_column(
        ForeignKey("quests.quest_id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    outcome: Mapped[str] = mapped_column(String, nullable=False)
    perceived_difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    energy_status: Mapped[str | None] = mapped_column(String, nullable=True)
    loot_type: Mapped[str | None] = mapped_column(String, nullable=True)
    mood_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_variation_seed: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    quest: Mapped[Quest] = relationship("Quest", back_populates="logs")
    goal: Mapped[Goal] = relationship("Goal", back_populates="quest_logs")


class Metric(Base):
    __tablename__ = "metrics"

    metric_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    metric_type: Mapped[str] = mapped_column(String, default="INCREMENTAL")
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    initial_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    progress: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=func.now()
    )

    goal: Mapped[Goal] = relationship("Goal", back_populates="metrics")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    goal_id: Mapped[str | None] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped[Goal | None] = relationship("Goal", back_populates="conversation_logs")


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    summary_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ConversationState(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    state_blob: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=func.now()
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    challenge_appetite: Mapped[str] = mapped_column(String, default="MEDIUM")
    theme_preference: Mapped[str] = mapped_column(String, default="GAME")
    onboarding_stage: Mapped[str] = mapped_column(
        String, default="STAGE_0_ONBOARDING"
    )
    personality_type: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_playstyle: Mapped[str | None] = mapped_column(String, nullable=True)
    calm_time_window: Mapped[str | None] = mapped_column(Text, nullable=True)
    disliked_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PlayerProgress(Base):
    __tablename__ = "player_progress"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    focus_goal_id: Mapped[str | None] = mapped_column(String, nullable=True)
    stage_label: Mapped[str] = mapped_column(
        String, default="STAGE_0_ONBOARDING"
    )
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience_points: Mapped[int] = mapped_column(Integer, default=0)
    streak_weeks: Mapped[int] = mapped_column(Integer, default=0)
    last_reflection_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Reminder(Base):
    __tablename__ = "reminders"

    reminder_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String, default="slack")
    frequency: Mapped[str] = mapped_column(String, default="daily")
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    preferred_time: Mapped[str | None] = mapped_column(String, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=func.now()
    )
    goal: Mapped[Goal] = relationship("Goal", back_populates="reminders")


class LLMUsageLedger(Base):
    __tablename__ = "llm_usage_ledger"

    entry_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    conversation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class LLMUsageDaily(Base):
    __tablename__ = "llm_daily_usage"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


__all__ = [
    "Base",
    "Goal",
    "BossStage",
    "Quest",
    "QuestLog",
    "UserPreference",
    "PlayerProgress",
    "Reminder",
    "Metric",
    "ConversationState",
    "ConversationLog",
    "ConversationSummary",
    "LLMUsageLedger",
    "LLMUsageDaily",
]
