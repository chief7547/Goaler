"""In-memory storage adapter for Goaler."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional


@dataclass
class BossStage:
    boss_id: str
    goal_id: str
    title: str
    description: Optional[str] = None
    success_criteria: Optional[str] = None
    stage_order: int = 0
    status: str = "PLANNED"
    target_week: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Quest:
    quest_id: str
    goal_id: str
    title: str
    description: Optional[str] = None
    difficulty_tier: str = "NORMAL"
    expected_duration_minutes: Optional[int] = None
    variation_tags: List[str] = field(default_factory=list)
    is_custom: bool = False
    origin_prompt_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QuestLog:
    log_id: str
    quest_id: str
    goal_id: str
    occurred_at: str
    outcome: str
    perceived_difficulty: Optional[str] = None
    energy_status: Optional[str] = None
    loot_type: Optional[str] = None
    mood_note: Optional[str] = None
    llm_variation_seed: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class InMemoryStorage:
    """Lightweight storage implementation backed by process memory."""

    def __init__(self) -> None:
        self._boss_stages: Dict[str, BossStage] = {}
        self._boss_by_goal: Dict[str, List[str]] = {}
        self._quests: Dict[str, Quest] = {}
        self._quest_logs: Dict[str, QuestLog] = {}

    # ------------------------------------------------------------------
    # Boss stages
    # ------------------------------------------------------------------
    def create_boss_stage(self, goal_id: str, payload: dict) -> dict:
        boss_id = payload.get("boss_id") or str(uuid.uuid4())
        stage = BossStage(
            boss_id=boss_id,
            goal_id=goal_id,
            title=payload["title"],
            description=payload.get("description"),
            success_criteria=payload.get("success_criteria"),
            stage_order=payload.get("stage_order", 0),
            status=payload.get("status", "PLANNED"),
            target_week=payload.get("target_week"),
        )
        self._boss_stages[boss_id] = stage
        self._boss_by_goal.setdefault(goal_id, []).append(boss_id)
        return stage.to_dict()

    def list_boss_stages(self, goal_id: str) -> List[dict]:
        ids = self._boss_by_goal.get(goal_id, [])
        stages = [self._boss_stages[boss_id] for boss_id in ids]
        stages.sort(key=lambda item: (item.stage_order, item.title))
        return [stage.to_dict() for stage in stages]

    # ------------------------------------------------------------------
    # Quests
    # ------------------------------------------------------------------
    def create_quest(self, goal_id: str, payload: dict) -> dict:
        quest_id = payload.get("quest_id") or str(uuid.uuid4())
        quest = Quest(
            quest_id=quest_id,
            goal_id=goal_id,
            title=payload["title"],
            description=payload.get("description"),
            difficulty_tier=payload.get("difficulty_tier", "NORMAL"),
            expected_duration_minutes=payload.get("expected_duration_minutes"),
            variation_tags=list(payload.get("variation_tags", [])),
            is_custom=payload.get("is_custom", False),
            origin_prompt_hash=payload.get("origin_prompt_hash"),
        )
        self._quests[quest_id] = quest
        return quest.to_dict()

    # ------------------------------------------------------------------
    # Quest logs
    # ------------------------------------------------------------------
    def log_quest_event(self, payload: dict) -> dict:
        log_id = payload.get("log_id") or str(uuid.uuid4())
        log = QuestLog(
            log_id=log_id,
            quest_id=payload["quest_id"],
            goal_id=payload["goal_id"],
            occurred_at=payload["occurred_at"],
            outcome=payload["outcome"],
            perceived_difficulty=payload.get("perceived_difficulty"),
            energy_status=payload.get("energy_status"),
            loot_type=payload.get("loot_type"),
            mood_note=payload.get("mood_note"),
            llm_variation_seed=payload.get("llm_variation_seed"),
        )
        self._quest_logs[log_id] = log
        return log.to_dict()

    def list_recent_quest_logs(self, goal_id: str, limit: int = 10) -> List[dict]:
        filtered = [log for log in self._quest_logs.values() if log.goal_id == goal_id]
        filtered.sort(key=lambda entry: entry.occurred_at, reverse=True)
        return [log.to_dict() for log in filtered[:limit]]


__all__ = ["InMemoryStorage"]
