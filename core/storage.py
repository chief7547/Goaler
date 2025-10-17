"""SQLAlchemy-backed storage implementation for Goaler."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Iterable

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, BossStage, Goal, Quest, QuestLog


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
        goal = Goal(
            title=payload["title"],
            goal_type=payload.get("goal_type", "ONE_TIME"),
            motivation=payload.get("motivation"),
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
            "title": goal.title,
            "goal_type": goal.goal_type,
            "motivation": goal.motivation,
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


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    url = database_url or os.getenv("GOALER_DATABASE_URL", "sqlite:///data/goaler.db")
    if url.startswith("sqlite:///") and not url.startswith("sqlite:///:memory:"):
        db_path = url.replace("sqlite:///", "", 1)
        directory = os.path.dirname(db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def create_session(database_url: str | None = None) -> Session:
    factory = create_session_factory(database_url)
    return factory()


__all__ = [
    "SQLAlchemyStorage",
    "create_session",
    "create_session_factory",
]
