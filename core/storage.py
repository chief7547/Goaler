"""SQLAlchemy-backed storage implementation for Goaler."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import create_engine, select, text, func, delete
from sqlalchemy.orm import Session, sessionmaker

from .models import (
    Base,
    BossStage,
    ConversationLog,
    ConversationState,
    ConversationSummary,
    Goal,
    Metric,
    PlayerProgress,
    Quest,
    QuestLog,
    Reminder,
    UserPreference,
)
from .privacy import sanitize_note


def _tags_to_string(tags: Iterable[str] | None) -> str | None:
    if not tags:
        return None
    values = [entry for entry in tags if entry]
    if not values:
        return None
    return ",".join(values)


def _tags_from_string(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [entry for entry in raw.split(",") if entry]


def _list_to_string(items: Iterable[str] | None) -> str | None:
    if items is None:
        return None
    values = [item for item in items if item]
    if not values:
        return None
    return ",".join(values)


def _string_to_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [entry for entry in raw.split(",") if entry]


def _coerce_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError("occurred_at must be datetime or ISO formatted string")


def _coerce_optional_datetime(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    return _coerce_datetime(value)


def _json_default(value):  # pragma: no cover - defensive serializer
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


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
            conversation_id=payload.get("conversation_id"),
            deadline=_coerce_optional_datetime(payload.get("deadline")),
            status=payload.get("status", "IN_PROGRESS"),
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

    def update_goal(self, goal_id: str, payload: dict) -> dict | None:
        goal = self.session.get(Goal, goal_id)
        if goal is None:
            return None
        for field in (
            "title",
            "goal_type",
            "motivation",
            "deadline",
            "status",
            "conversation_id",
            "completed_at",
        ):
            if field in payload:
                if field in {"deadline", "completed_at"}:
                    setattr(goal, field, _coerce_optional_datetime(payload[field]))
                else:
                    setattr(goal, field, payload[field])
        self.session.commit()
        self.session.refresh(goal)
        return self._goal_to_dict(goal)

    def _goal_to_dict(self, goal: Goal) -> dict:
        return {
            "goal_id": goal.goal_id,
            "user_id": goal.user_id,
            "title": goal.title,
            "goal_type": goal.goal_type,
            "motivation": goal.motivation,
            "conversation_id": goal.conversation_id,
            "deadline": goal.deadline.isoformat() if goal.deadline else None,
            "status": goal.status,
            "created_at": goal.created_at.isoformat(),
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None,
            "completed_at": goal.completed_at.isoformat()
            if goal.completed_at
            else None,
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
            "personality_type": record.personality_type,
            "preferred_playstyle": record.preferred_playstyle,
            "calm_time_window": _string_to_list(record.calm_time_window),
            "disliked_patterns": _string_to_list(record.disliked_patterns),
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
                personality_type=payload.get("personality_type"),
                preferred_playstyle=payload.get("preferred_playstyle"),
                calm_time_window=_list_to_string(payload.get("calm_time_window")),
                disliked_patterns=_list_to_string(payload.get("disliked_patterns")),
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
            if "personality_type" in payload:
                record.personality_type = payload["personality_type"]
            if "preferred_playstyle" in payload:
                record.preferred_playstyle = payload["preferred_playstyle"]
            if "calm_time_window" in payload:
                record.calm_time_window = _list_to_string(payload.get("calm_time_window"))
            if "disliked_patterns" in payload:
                record.disliked_patterns = _list_to_string(payload.get("disliked_patterns"))
            record.updated_at = timestamp
        self.session.commit()
        self.session.refresh(record)
        return {
            "user_id": record.user_id,
            "challenge_appetite": record.challenge_appetite,
            "theme_preference": record.theme_preference,
            "onboarding_stage": record.onboarding_stage,
            "personality_type": record.personality_type,
            "preferred_playstyle": record.preferred_playstyle,
            "calm_time_window": _string_to_list(record.calm_time_window),
            "disliked_patterns": _string_to_list(record.disliked_patterns),
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
    # Conversation state snapshots
    # ------------------------------------------------------------------
    def save_conversation_state(
        self,
        conversation_id: str,
        state: dict,
        *,
        user_id: str | None = None,
        status: str = "ACTIVE",
    ) -> dict:
        record = self.session.get(ConversationState, conversation_id)
        timestamp = datetime.now(timezone.utc)
        if record is None:
            record = ConversationState(
                conversation_id=conversation_id,
                user_id=user_id,
                status=status,
                state_blob=json.dumps(state, ensure_ascii=False, default=_json_default),
                created_at=timestamp,
                updated_at=timestamp,
            )
            self.session.add(record)
        else:
            if user_id is not None:
                record.user_id = user_id
            record.status = status
            record.state_blob = json.dumps(state, ensure_ascii=False, default=_json_default)
            record.updated_at = timestamp
        self.session.commit()
        self.session.refresh(record)
        return self._conversation_state_to_dict(record)

    def get_conversation_state(self, conversation_id: str) -> dict | None:
        record = self.session.get(ConversationState, conversation_id)
        if record is None:
            return None
        return self._conversation_state_to_dict(record)

    def delete_conversation_state(self, conversation_id: str) -> None:
        record = self.session.get(ConversationState, conversation_id)
        if record is None:
            return
        self.session.delete(record)
        self.session.commit()

    def _conversation_state_to_dict(self, record: ConversationState) -> dict:
        return {
            "conversation_id": record.conversation_id,
            "user_id": record.user_id,
            "status": record.status,
            "state": json.loads(record.state_blob) if record.state_blob else None,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def create_metric(self, goal_id: str, payload: dict) -> dict:
        metric = Metric(
            goal_id=goal_id,
            metric_name=payload["metric_name"],
            metric_type=payload.get("metric_type", "INCREMENTAL"),
            target_value=payload.get("target_value"),
            unit=payload.get("unit"),
            initial_value=payload.get("initial_value"),
            progress=payload.get("progress"),
        )
        self.session.add(metric)
        self.session.commit()
        self.session.refresh(metric)
        return self._metric_to_dict(metric)

    def list_metrics(self, goal_id: str) -> list[dict]:
        stmt = select(Metric).where(Metric.goal_id == goal_id).order_by(Metric.created_at)
        metrics = self.session.scalars(stmt).all()
        return [self._metric_to_dict(metric) for metric in metrics]

    def _metric_to_dict(self, metric: Metric) -> dict:
        return {
            "metric_id": metric.metric_id,
            "goal_id": metric.goal_id,
            "metric_name": metric.metric_name,
            "metric_type": metric.metric_type,
            "target_value": metric.target_value,
            "unit": metric.unit,
            "initial_value": metric.initial_value,
            "progress": metric.progress,
            "created_at": metric.created_at.isoformat(),
            "updated_at": metric.updated_at.isoformat(),
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
            "created_at": quest.created_at.isoformat(),
            "updated_at": quest.updated_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Quest logs
    # ------------------------------------------------------------------
    def log_quest_event(self, payload: dict) -> dict:
        log = QuestLog(
            quest_id=payload["quest_id"],
            goal_id=payload["goal_id"],
            occurred_at=_coerce_datetime(payload.get("occurred_at", datetime.now(timezone.utc))),
            outcome=payload["outcome"],
            perceived_difficulty=payload.get("perceived_difficulty"),
            energy_status=payload.get("energy_status"),
            loot_type=payload.get("loot_type"),
            mood_note=sanitize_note(payload.get("mood_note")),
            llm_variation_seed=payload.get("llm_variation_seed"),
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
            "created_at": log.created_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------
    def create_conversation_log(self, payload: dict) -> dict:
        log = ConversationLog(
            conversation_id=payload["conversation_id"],
            goal_id=payload.get("goal_id"),
            role=payload["role"],
            content=payload["content"],
            token_count=payload.get("token_count"),
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return self._conversation_log_to_dict(log)

    def list_conversation_logs(self, conversation_id: str, limit: int = 50) -> list[dict]:
        stmt = (
            select(ConversationLog)
            .where(ConversationLog.conversation_id == conversation_id)
            .order_by(ConversationLog.created_at.desc())
            .limit(limit)
        )
        rows = self.session.scalars(stmt).all()
        return [self._conversation_log_to_dict(row) for row in rows]

    def count_conversation_logs(self, conversation_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(ConversationLog)
            .where(ConversationLog.conversation_id == conversation_id)
        )
        result = self.session.execute(stmt).scalar()
        return int(result or 0)

    def trim_conversation_logs(self, conversation_id: str, keep_latest: int = 10) -> int:
        if keep_latest < 0:
            keep_latest = 0
        keep_stmt = (
            select(ConversationLog.log_id)
            .where(ConversationLog.conversation_id == conversation_id)
            .order_by(ConversationLog.created_at.desc(), ConversationLog.log_id.desc())
            .limit(keep_latest)
        )
        ids_to_keep = [row[0] for row in self.session.execute(keep_stmt)]

        delete_stmt = delete(ConversationLog).where(
            ConversationLog.conversation_id == conversation_id
        )
        if ids_to_keep:
            delete_stmt = delete_stmt.where(~ConversationLog.log_id.in_(ids_to_keep))

        result = self.session.execute(delete_stmt)
        self.session.commit()
        return int(result.rowcount or 0)

    def create_conversation_summary(self, payload: dict) -> dict:
        summary = ConversationSummary(
            conversation_id=payload["conversation_id"],
            period_start=_coerce_optional_datetime(payload.get("period_start")),
            period_end=_coerce_optional_datetime(payload.get("period_end")),
            summary_text=payload["summary_text"],
        )
        self.session.add(summary)
        self.session.commit()
        self.session.refresh(summary)
        return self._conversation_summary_to_dict(summary)

    def list_conversation_summaries(self, conversation_id: str) -> list[dict]:
        stmt = (
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
            .order_by(ConversationSummary.created_at.desc())
        )
        rows = self.session.scalars(stmt).all()
        return [self._conversation_summary_to_dict(row) for row in rows]

    def _conversation_log_to_dict(self, log: ConversationLog) -> dict:
        return {
            "log_id": log.log_id,
            "conversation_id": log.conversation_id,
            "goal_id": log.goal_id,
            "role": log.role,
            "content": log.content,
            "token_count": log.token_count,
            "created_at": log.created_at.isoformat(),
        }

    def _conversation_summary_to_dict(self, summary: ConversationSummary) -> dict:
        return {
            "summary_id": summary.summary_id,
            "conversation_id": summary.conversation_id,
            "period_start": summary.period_start.isoformat()
            if summary.period_start
            else None,
            "period_end": summary.period_end.isoformat() if summary.period_end else None,
            "summary_text": summary.summary_text,
            "created_at": summary.created_at.isoformat(),
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
            "updated_at": reminder.updated_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Stage progression helpers
    # ------------------------------------------------------------------
    def get_stage_counters(self, user_id: str) -> dict[str, int]:
        stmt = (
            select(
                func.count().filter(QuestLog.outcome == "COMPLETED").label("completed"),
                func.count().filter(QuestLog.loot_type.is_not(None)).label("loot"),
                func.count().filter(QuestLog.energy_status.is_not(None)).label("energy"),
            )
            .select_from(QuestLog)
            .join(Goal, QuestLog.goal_id == Goal.goal_id)
            .where(Goal.user_id == user_id)
        )
        completed = loot = energy = 0
        result = self.session.execute(stmt).first()
        if result is not None:
            completed = int(result.completed or 0)
            loot = int(result.loot or 0)
            energy = int(result.energy or 0)
        return {
            "completed": completed,
            "loot": loot,
            "energy": energy,
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
        _auto_upgrade_schema(engine)

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


def _auto_upgrade_schema(engine) -> None:
    """Apply lightweight in-place migrations for SQLite deployments."""

    if not engine.url.drivername.startswith("sqlite"):
        return

    with engine.begin() as conn:  # type: ignore[call-arg]
        def column_exists(table: str, column: str) -> bool:
            result = conn.execute(text(f"PRAGMA table_info({table})"))
            return any(row[1] == column for row in result.fetchall())

        def ensure_column(table: str, column: str, ddl: str) -> None:
            if column_exists(table, column):
                return
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))

        ensure_column("goals", "conversation_id", "VARCHAR")
        ensure_column("goals", "deadline", "TIMESTAMP")
        ensure_column("goals", "status", "VARCHAR DEFAULT 'IN_PROGRESS'")
        ensure_column("goals", "updated_at", "TIMESTAMP")
        ensure_column("goals", "completed_at", "TIMESTAMP")

        ensure_column("quests", "updated_at", "TIMESTAMP")
        ensure_column("quest_logs", "created_at", "TIMESTAMP")

        ensure_column("user_preferences", "personality_type", "VARCHAR")
        ensure_column("user_preferences", "preferred_playstyle", "VARCHAR")
        ensure_column("user_preferences", "calm_time_window", "TEXT")
        ensure_column("user_preferences", "disliked_patterns", "TEXT")

        ensure_column("reminders", "updated_at", "TIMESTAMP")

        # Ensure new tables exist (no-op if already created)
        Base.metadata.create_all(engine, tables=[
            Base.metadata.tables["metrics"],
            Base.metadata.tables["conversation_logs"],
            Base.metadata.tables["conversation_summaries"],
            Base.metadata.tables["conversations"],
        ])


__all__ = [
    "SQLAlchemyStorage",
    "create_session",
    "create_session_factory",
]
