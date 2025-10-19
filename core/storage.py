"""SQLAlchemy-backed storage implementation for Goaler."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from .models import (
    Base,
    BossStage,
    Goal,
    PlayerProgress,
    Quest,
    QuestLog,
    Reminder,
    UserPreference,
)


def _tags_to_string(tags: Iterable[str] | None) -> str | None:
    if not tags:
        return None
    return ",".join(tags)


def _tags_from_string(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [entry for entry in raw.split(",") if entry]


def _coerce_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError("occurred_at must be datetime or ISO formatted string")


class SQLAlchemyStorage:
    """Lightweight CRUD wrapper around a SQLAlchemy session."""

    def __init__(self, session: Session):
        self.session = session

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------
    def create_goal(self, payload: dict) -> dict:
        if "user_id" not in payload or not payload["user_id"]:
            raise ValueError("user_id is required when creating a goal")
        goal = Goal(
            title=payload["title"],
            goal_type=payload.get("goal_type", "ONE_TIME"),
            motivation=payload.get("motivation"),
            user_id=payload["user_id"],
        )
        self.session.add(goal)
        self.session.commit()
        self.session.refresh(goal)
        return self._goal_to_dict(goal)

    def get_goal(self, goal_id: str) -> dict | None:
        goal = self.session.get(Goal, goal_id)
        if not goal:
            return None
        return self._goal_to_dict(goal)

    def _goal_to_dict(self, goal: Goal) -> dict:
        return {
            "goal_id": goal.goal_id,
            "user_id": goal.user_id,
            "title": goal.title,
            "goal_type": goal.goal_type,
            "motivation": goal.motivation,
        }

    # ------------------------------------------------------------------
    # User preferences
    # ------------------------------------------------------------------
    def get_user_preferences(self, user_id: str) -> dict | None:
        record = self.session.get(UserPreference, user_id)
        if not record:
            return None
        return {
            "user_id": record.user_id,
            "challenge_appetite": record.challenge_appetite,
            "theme_preference": record.theme_preference,
            "onboarding_stage": record.onboarding_stage,
        }

    def save_user_preferences(self, payload: dict) -> dict:
        user_id = payload["user_id"]
        record = self.session.get(UserPreference, user_id)
        timestamp = datetime.now(timezone.utc)
        if record is None:
            record = UserPreference(
                user_id=user_id,
                challenge_appetite=payload.get("challenge_appetite", "MEDIUM"),
                theme_preference=payload.get("theme_preference", "GAME"),
                onboarding_stage=payload.get("onboarding_stage", "STAGE_0_ONBOARDING"),
                updated_at=timestamp,
            )
            self.session.add(record)
        else:
            if "challenge_appetite" in payload:
                record.challenge_appetite = payload["challenge_appetite"]
            if "theme_preference" in payload:
                record.theme_preference = payload["theme_preference"]
            if "onboarding_stage" in payload:
                record.onboarding_stage = payload["onboarding_stage"]
            record.updated_at = timestamp
        self.session.commit()
        self.session.refresh(record)
        return {
            "user_id": record.user_id,
            "challenge_appetite": record.challenge_appetite,
            "theme_preference": record.theme_preference,
            "onboarding_stage": record.onboarding_stage,
        }

    # ------------------------------------------------------------------
    # Player progress
    # ------------------------------------------------------------------
    def get_player_progress(self, user_id: str) -> dict | None:
        record = self.session.get(PlayerProgress, user_id)
        if not record:
            return None
        return self._player_progress_to_dict(record)

    def upsert_player_progress(self, payload: dict) -> dict:
        user_id = payload["user_id"]
        record = self.session.get(PlayerProgress, user_id)
        timestamp = datetime.now(timezone.utc)
        if record is None:
            record = PlayerProgress(
                user_id=user_id,
                focus_goal_id=payload.get("focus_goal_id"),
                stage_label=payload.get("stage_label", "STAGE_0_ONBOARDING"),
                level=payload.get("level", 1),
                experience_points=payload.get("experience_points", 0),
                streak_weeks=payload.get("streak_weeks", 0),
                last_reflection_at=payload.get("last_reflection_at"),
                updated_at=timestamp,
            )
            self.session.add(record)
        else:
            for field in (
                "focus_goal_id",
                "stage_label",
                "level",
                "experience_points",
                "streak_weeks",
                "last_reflection_at",
            ):
                if field in payload:
                    setattr(record, field, payload[field])
            record.updated_at = timestamp
        self.session.commit()
        self.session.refresh(record)
        return self._player_progress_to_dict(record)

    def update_player_progress(self, user_id: str, payload: dict) -> dict:
        payload_with_id = dict(payload)
        payload_with_id["user_id"] = user_id
        return self.upsert_player_progress(payload_with_id)

    def _player_progress_to_dict(self, record: PlayerProgress) -> dict:
        return {
            "user_id": record.user_id,
            "focus_goal_id": record.focus_goal_id,
            "stage_label": record.stage_label,
            "level": record.level,
            "experience_points": record.experience_points,
            "streak_weeks": record.streak_weeks,
            "last_reflection_at": record.last_reflection_at.isoformat()
            if record.last_reflection_at
            else None,
            "updated_at": record.updated_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Boss stages
    # ------------------------------------------------------------------
    def create_boss_stage(self, goal_id: str, payload: dict) -> dict:
        stage = BossStage(
            goal_id=goal_id,
            title=payload["title"],
            description=payload.get("description"),
            success_criteria=payload.get("success_criteria"),
            stage_order=payload.get("stage_order", 0),
            status=payload.get("status", "PLANNED"),
            target_week=payload.get("target_week"),
            boss_id=payload.get("boss_id", str(uuid.uuid4())),
        )
        self.session.add(stage)
        self.session.commit()
        self.session.refresh(stage)
        return self._boss_stage_to_dict(stage)

    def list_boss_stages(self, goal_id: str) -> list[dict]:
        stmt = (
            select(BossStage)
            .where(BossStage.goal_id == goal_id)
            .order_by(BossStage.stage_order, BossStage.created_at)
        )
        stages = self.session.scalars(stmt).all()
        return [self._boss_stage_to_dict(stage) for stage in stages]

    def _boss_stage_to_dict(self, stage: BossStage) -> dict:
        return {
            "boss_id": stage.boss_id,
            "goal_id": stage.goal_id,
            "title": stage.title,
            "description": stage.description,
            "success_criteria": stage.success_criteria,
            "stage_order": stage.stage_order,
            "status": stage.status,
            "target_week": stage.target_week,
        }

    # ------------------------------------------------------------------
    # Quests
    # ------------------------------------------------------------------
    def create_quest(self, goal_id: str, payload: dict) -> dict:
        quest = Quest(
            goal_id=goal_id,
            title=payload["title"],
            description=payload.get("description"),
            difficulty_tier=payload.get("difficulty_tier", "NORMAL"),
            expected_duration_minutes=payload.get("expected_duration_minutes"),
            variation_tags=_tags_to_string(payload.get("variation_tags")),
            is_custom=bool(payload.get("is_custom", False)),
            origin_prompt_hash=payload.get("origin_prompt_hash"),
            quest_id=payload.get("quest_id", str(uuid.uuid4())),
        )
        self.session.add(quest)
        self.session.commit()
        self.session.refresh(quest)
        return self._quest_to_dict(quest)

    def get_quest(self, quest_id: str) -> dict | None:
        quest = self.session.get(Quest, quest_id)
        if not quest:
            return None
        return self._quest_to_dict(quest)

    def _quest_to_dict(self, quest: Quest) -> dict:
        return {
            "quest_id": quest.quest_id,
            "goal_id": quest.goal_id,
            "title": quest.title,
            "description": quest.description,
            "difficulty_tier": quest.difficulty_tier,
            "expected_duration_minutes": quest.expected_duration_minutes,
            "variation_tags": _tags_from_string(quest.variation_tags),
            "is_custom": quest.is_custom,
            "origin_prompt_hash": quest.origin_prompt_hash,
        }

    # ------------------------------------------------------------------
    # Quest logs
    # ------------------------------------------------------------------
    def log_quest_event(self, payload: dict) -> dict:
        log = QuestLog(
            quest_id=payload["quest_id"],
            goal_id=payload["goal_id"],
            occurred_at=_coerce_datetime(payload["occurred_at"]),
            outcome=payload["outcome"],
            perceived_difficulty=payload.get("perceived_difficulty"),
            energy_status=payload.get("energy_status"),
            loot_type=payload.get("loot_type"),
            mood_note=payload.get("mood_note"),
            llm_variation_seed=payload.get("llm_variation_seed"),
            log_id=payload.get("log_id", str(uuid.uuid4())),
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return self._quest_log_to_dict(log)

    def list_recent_quest_logs(self, goal_id: str, limit: int = 10) -> list[dict]:
        stmt = (
            select(QuestLog)
            .where(QuestLog.goal_id == goal_id)
            .order_by(QuestLog.occurred_at.desc())
            .limit(limit)
        )
        logs = self.session.scalars(stmt).all()
        return [self._quest_log_to_dict(log) for log in logs]

    def _quest_log_to_dict(self, log: QuestLog) -> dict:
        return {
            "log_id": log.log_id,
            "quest_id": log.quest_id,
            "goal_id": log.goal_id,
            "occurred_at": log.occurred_at.isoformat(),
            "outcome": log.outcome,
            "perceived_difficulty": log.perceived_difficulty,
            "energy_status": log.energy_status,
            "loot_type": log.loot_type,
            "mood_note": log.mood_note,
            "llm_variation_seed": log.llm_variation_seed,
        }

    # ------------------------------------------------------------------
    # Reminders
    # ------------------------------------------------------------------
    def create_reminder(self, payload: dict) -> dict:
        reminder = Reminder(
            goal_id=payload["goal_id"],
            channel=payload.get("channel", "slack"),
            frequency=payload.get("frequency", "daily"),
            next_run_at=payload.get("next_run_at"),
            preferred_time=payload.get("preferred_time"),
            active=payload.get("active", True),
            reminder_id=payload.get("reminder_id", str(uuid.uuid4())),
        )
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        return self._reminder_to_dict(reminder)

    def list_reminders_due(self, now: datetime) -> list[dict]:
        stmt = (
            select(Reminder)
            .where(Reminder.active.is_(True))
            .where(Reminder.next_run_at.is_not(None))
            .where(Reminder.next_run_at <= now)
        )
        reminders = self.session.scalars(stmt).all()
        return [self._reminder_to_dict(reminder) for reminder in reminders]

    def update_reminder(self, reminder_id: str, payload: dict) -> dict | None:
        reminder = self.session.get(Reminder, reminder_id)
        if reminder is None:
            return None
        for field in ("channel", "frequency", "next_run_at", "preferred_time", "active"):
            if field in payload:
                setattr(reminder, field, payload[field])
        self.session.commit()
        self.session.refresh(reminder)
        return self._reminder_to_dict(reminder)

    def _reminder_to_dict(self, reminder: Reminder) -> dict:
        return {
            "reminder_id": reminder.reminder_id,
            "goal_id": reminder.goal_id,
            "channel": reminder.channel,
            "frequency": reminder.frequency,
            "next_run_at": reminder.next_run_at.isoformat()
            if reminder.next_run_at
            else None,
            "preferred_time": reminder.preferred_time,
            "active": reminder.active,
        }


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    url = database_url or os.getenv("GOALER_DATABASE_URL") or "sqlite:///data/goaler.db"

    engine_kwargs: dict = {"future": True, "pool_pre_ping": True}

    if url.startswith("sqlite:///"):
        if not url.startswith("sqlite:///:memory:"):
            db_path = url.replace("sqlite:///", "", 1)
            directory = os.path.dirname(db_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
        engine_kwargs.setdefault("connect_args", {})["check_same_thread"] = False
    else:
        pool_size = _as_int_env("GOALER_DB_POOL_SIZE")
        if pool_size:
            engine_kwargs["pool_size"] = pool_size
        max_overflow = _as_int_env("GOALER_DB_MAX_OVERFLOW")
        if max_overflow is not None:
            engine_kwargs["max_overflow"] = max_overflow

    engine = create_engine(url, **engine_kwargs)

    if _should_autocreate_schema():
        Base.metadata.create_all(engine)

    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def create_session(database_url: str | None = None) -> Session:
    factory = create_session_factory(database_url)
    return factory()


def _should_autocreate_schema() -> bool:
    flag = os.getenv("GOALER_AUTO_CREATE_SCHEMA", "true").strip().lower()
    return flag not in {"0", "false", "no"}


def _as_int_env(name: str) -> int | None:
    value = os.getenv(name)
    if not value:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed


__all__ = [
    "SQLAlchemyStorage",
    "create_session",
    "create_session_factory",
]
