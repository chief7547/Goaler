"""SQLAlchemy models for Goaler."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class Goal(Base):
    __tablename__ = "goals"

    goal_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, default="default_user")
    title: Mapped[str] = mapped_column(String, nullable=False)
    goal_type: Mapped[str] = mapped_column(String, default="ONE_TIME")
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    boss_stages: Mapped[list["BossStage"]] = relationship(
        "BossStage", cascade="all, delete-orphan", back_populates="goal"
    )
    quests: Mapped[list["Quest"]] = relationship(
        "Quest", cascade="all, delete-orphan", back_populates="goal"
    )


class BossStage(Base):
    __tablename__ = "boss_stages"

    boss_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False
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
        ForeignKey("goals.goal_id", ondelete="CASCADE"), nullable=False
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

    goal: Mapped[Goal] = relationship("Goal", back_populates="quests")
    logs: Mapped[list["QuestLog"]] = relationship(
        "QuestLog", cascade="all, delete-orphan", back_populates="quest"
    )


class QuestLog(Base):
    __tablename__ = "quest_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    quest_id: Mapped[str] = mapped_column(
        ForeignKey("quests.quest_id", ondelete="CASCADE"), nullable=False
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

    quest: Mapped[Quest] = relationship("Quest", back_populates="logs")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    challenge_appetite: Mapped[str] = mapped_column(String, default="MEDIUM")
    theme_preference: Mapped[str] = mapped_column(String, default="GAME")


__all__ = [
    "Base",
    "Goal",
    "BossStage",
    "Quest",
    "QuestLog",
    "UserPreference",
]
