"""Core agent that orchestrates the goal-setting conversation."""

from __future__ import annotations

from datetime import datetime, timezone
from textwrap import dedent
from typing import Any, Iterable

from .coach import CoachResponder, ToneContext
from .storage import SQLAlchemyStorage, create_session
from .user_preferences import ContextLoader

from .state_manager import StateManager

STAGE_0 = "STAGE_0_ONBOARDING"


def _default_feature_flags() -> dict[str, bool]:
    """Return feature exposure flags for the initial onboarding stage."""

    return {
        "loot": False,
        "energy": False,
        "boss": False,
    }


def _coerce_metric_details(
    metric_details: dict | None,
    metric_kwargs: dict,
) -> dict | None:
    """Normalize metric payloads coming from the LLM tool call."""

    if metric_details is not None:
        return metric_details

    if not metric_kwargs:
        return None

    allowed = {"metric_name", "metric_type", "target_value", "unit", "initial_value"}
    filtered = {key: value for key, value in metric_kwargs.items() if key in allowed}
    required = {"metric_name", "metric_type", "target_value", "unit"}

    if required.issubset(filtered):
        return filtered

    return None


SYSTEM_PROMPT = dedent(
    """
    # Persona
    You are Goaler, an AI growth coach who blends strategy, empathy, and playfulness.
    Your default tone is warm, concise, and practical. Adapt your flavour to the
    context:
      - If `user_preferences.challenge_appetite` is HIGH → adventurous tone.
      - If it is LOW → gentle and incremental guidance.
      - If `energy_status` is NEEDS_POTION → soft, recovery-first tone.
      - ACHIEVEMENT → celebrate; INSIGHT → highlight the lesson; EMOTION → validate feelings.
    See docs/COACH_TONE_GUIDE.md for tone examples.

    # Temporal awareness
    • Morning: energising, mention upcoming boss preparation.
    • Midday: check-in on progress; prompt for small wins.
    • Evening: recap and invite reflection/loot.

    # Core Task
    Guide the user through a natural conversation to define and execute a real-world
    goal. Build a structured plan incrementally by calling the available tools.
    Never demand all information at once—advance step by step.

    # Dialogue Principles
    • Start each turn with a short acknowledgement ("Great job", "알겠습니다") before guidance.
    • Reflect the latest `boss_stages`, weekly steps, quest outcomes, or loot entries.
    • Low energy → recovery suggestions first; READY_FOR_BOSS → bold, strategic actions aligned
      with the next boss stage.
    • Encourage loot logging as “전리품 덱” 기록, emphasising its future use in reports.

    # Rules
    1. Call `create_goal` when a new goal is requested.
    2. Collect measurable details and use `add_metric` for each metric you discover.
    3. Call `define_boss_stages`, `propose_weekly_plan`, and `propose_daily_tasks` to break the
       goal into meaningful real-world boss stages, weekly steps, and daily quests.
    4. Resolve ambiguity before acting. Ask clarifying questions when the request is unclear.
       - Example: “I want to run 5km.” → clarify whether it is a one-time target or recurring habit.
       - Example: Vague numbers or goals → ask for specific targets or units.
    5. Ask about the user's motivation at a natural point, then call `set_motivation`.
    6. After each change, briefly confirm what changed and summarise the current plan.
    7. When the user is satisfied, call `finalize_goal` to complete the process and
       send them off with an encouraging closing note.
    """
)


class GoalSettingAgent:
    """Manage the conversation state while responding to tool calls."""

    def __init__(
        self,
        *,
        storage: SQLAlchemyStorage | None = None,
        coach_responder: CoachResponder | None = None,
    ) -> None:
        self.state_manager = StateManager()
        self.storage = storage or SQLAlchemyStorage(create_session())
        self.coach_responder = coach_responder or CoachResponder()
        self.context_loader = ContextLoader(self.storage)

    def create_goal(
        self,
        conversation_id: str,
        title: str,
        *,
        user_id: str | None = None,
    ) -> dict | None:
        """Initialise a new goal in the state manager."""

        user_id = user_id or "default_user"
        prefs = self.context_loader.get_user_preferences(user_id)
        goal_record = self.storage.create_goal({"title": title})
        initial_state: dict[str, Any] = {
            "user_id": user_id,
            "goal_id": goal_record["goal_id"],
            "goal_title": goal_record["title"],
            "metrics": [],
            "motivation": None,
            "onboarding_stage": STAGE_0,
            "feature_flags": _default_feature_flags(),
            "boss_stage_ids": [],
            "boss_stage_titles": {},
            "weekly_plan": {},
            "current_variations": [],
            "accepted_quests": [],
            "theme_preference": prefs.theme_preference,
            "challenge_appetite": prefs.challenge_appetite,
        }
        self.state_manager.new_conversation(conversation_id, initial_state)
        return self.state_manager.get_state(conversation_id)

    def add_metric(
        self,
        conversation_id: str,
        metric_details: dict | None = None,
        **metric_kwargs,
    ) -> dict | None:
        """Append a metric to the goal state if enough information is provided."""

        current_state = self.state_manager.get_state(conversation_id)
        if not current_state:
            return None

        normalized = _coerce_metric_details(metric_details, metric_kwargs)
        if normalized is None:
            # Nothing to add yet; keep the snapshot so the LLM can recover.
            return current_state

        current_state.setdefault("metrics", []).append(normalized)
        self.state_manager.update_state(conversation_id, current_state)
        return current_state

    def set_motivation(self, conversation_id: str, text: str) -> dict | None:
        """Record the motivation associated with the current goal."""

        current_state = self.state_manager.get_state(conversation_id)
        if not current_state:
            return None

        current_state["motivation"] = text
        self.state_manager.update_state(conversation_id, current_state)
        return current_state

    def finalize_goal(self, conversation_id: str) -> bool:
        """Log the final state and clear the conversation cache."""

        final_state = self.state_manager.get_state(conversation_id)
        print(
            "--- DB: Saving final state for"
            f" {conversation_id} to database: {final_state} ---"
        )
        self.state_manager.end_conversation(conversation_id)
        return True

    def get_onboarding_context(self, conversation_id: str) -> dict[str, Any]:
        """Expose onboarding stage and feature flags for UI/adapters."""

        current_state = self.state_manager.get_state(conversation_id) or {}
        stage = current_state.get("onboarding_stage", STAGE_0)
        feature_flags = {
            "loot": False,
            "energy": False,
            "boss": False,
        }
        feature_flags.update(current_state.get("feature_flags", {}))
        return {
            "onboarding_stage": stage,
            "feature_flags": feature_flags,
        }

    # ------------------------------------------------------------------
    # Boss stage / planning helpers
    # ------------------------------------------------------------------

    def define_boss_stages(
        self,
        conversation_id: str,
        goal_id: str,
        boss_candidates: Iterable[dict],
    ) -> dict:
        """Persist boss stages and update conversational snapshot."""

        current_state = self.state_manager.get_state(conversation_id) or {}
        existing = current_state.setdefault("boss_stage_ids", [])
        titles = current_state.setdefault("boss_stage_titles", {})

        goal_id = current_state.get("goal_id", goal_id)
        created: list[dict] = []
        next_order = len(existing) + 1
        for candidate in boss_candidates:
            payload = {**candidate}
            payload.setdefault("stage_order", next_order)
            next_order += 1
            stage_dict = self.storage.create_boss_stage(goal_id, payload)
            created.append(stage_dict)

        for stage_dict in created:
            existing.append(stage_dict["boss_id"])
            titles[stage_dict["boss_id"]] = stage_dict["title"]
        self.state_manager.update_state(conversation_id, current_state)
        return {"status": "ok", "boss_stages": created}

    def propose_weekly_plan(
        self,
        conversation_id: str,
        goal_id: str,
        boss_id: str,
        weekly_plan: Iterable[dict],
    ) -> dict:
        """Attach weekly plan entries to the current boss preparation."""

        current_state = self.state_manager.get_state(conversation_id) or {}
        weekly_map = current_state.setdefault("weekly_plan", {})
        entries = list(weekly_plan)
        weekly_map[boss_id] = entries
        self.state_manager.update_state(conversation_id, current_state)
        return {
            "status": "ok",
            "weekly_plan": entries,
        }

    def propose_daily_tasks(
        self,
        conversation_id: str,
        goal_id: str,
        weekly_step: dict,
        daily_tasks: Iterable[dict],
    ) -> dict:
        """Store pending daily variations for user confirmation."""

        current_state = self.state_manager.get_state(conversation_id) or {}
        entries = list(daily_tasks)
        current_state["current_variations"] = entries
        current_state["last_weekly_step"] = weekly_step
        self.state_manager.update_state(conversation_id, current_state)
        return {
            "status": "ok",
            "daily_tasks": entries,
        }

    def choose_quest(
        self,
        conversation_id: str,
        goal_id: str,
        quest_choice: dict,
    ) -> dict:
        """Confirm quest selection and persist via storage."""

        current_state = self.state_manager.get_state(conversation_id) or {}
        goal_id = current_state.get("goal_id", goal_id)
        quest = self.storage.create_quest(goal_id, quest_choice)
        current_state.setdefault("accepted_quests", []).append(quest["quest_id"])
        current_state["current_variations"] = []
        self.state_manager.update_state(conversation_id, current_state)
        return {
            "status": "ok",
            "quest": quest,
        }

    def log_quest_outcome(
        self,
        conversation_id: str,
        payload: dict,
    ) -> dict:
        """Record quest execution outcome in storage and update state."""

        payload = dict(payload)
        payload.setdefault("occurred_at", datetime.now(timezone.utc))
        log = self.storage.log_quest_event(payload)
        current_state = self.state_manager.get_state(conversation_id) or {}
        current_state.setdefault("quest_logs", []).append(log["log_id"])
        if payload.get("energy_status"):
            current_state["last_energy_status"] = payload["energy_status"]
        if payload.get("loot_type"):
            current_state["last_loot_type"] = payload["loot_type"]
        if payload.get("mood_note"):
            current_state["last_loot_title"] = payload["mood_note"]
        self.state_manager.update_state(conversation_id, current_state)
        return {
            "status": "ok",
            "log": log,
        }

    def propose_quests(
        self,
        conversation_id: str,
        goal_id: str,
        candidate_pool: Iterable[dict],
    ) -> dict:
        """Offer quest variations unless onboarding stage locks the feature."""

        context = self.get_onboarding_context(conversation_id)
        feature_flags = context["feature_flags"]
        if not feature_flags.get("loot"):
            return {
                "status": "locked",
                "reason": "ONBOARDING_STAGE_LOCKED",
            }

        variations: list[dict] = []
        for candidate in candidate_pool:
            variation = dict(candidate)
            variation.setdefault("reason", "기본 추천 변주")
            variation.setdefault("difficulty_tier", "NORMAL")
            variations.append(variation)

        current_state = self.state_manager.get_state(conversation_id) or {}
        current_state["current_variations"] = variations
        self.state_manager.update_state(conversation_id, current_state)
        return {
            "status": "ok",
            "variations": variations,
        }

    # ------------------------------------------------------------------
    # Coach persona utilities
    # ------------------------------------------------------------------

    def compose_coach_reply(
        self,
        conversation_id: str,
        *,
        time_of_day: str | None = None,
        boss_name: str | None = None,
        now: datetime | None = None,
    ) -> str:
        state = self.state_manager.get_state(conversation_id) or {}
        goal_id = state.get("goal_id")
        user_id = state.get("user_id", "default_user")
        prefs = self.context_loader.get_user_preferences(user_id)

        challenge_appetite = state.get("challenge_appetite") or prefs.challenge_appetite
        theme_preference = state.get("theme_preference") or prefs.theme_preference

        if boss_name is None and goal_id:
            titles = state.get("boss_stage_titles", {})
            ordered_ids = state.get("boss_stage_ids", [])
            if ordered_ids:
                boss_name = titles.get(ordered_ids[0])
            if boss_name is None:
                stages = self.storage.list_boss_stages(goal_id)
                if stages:
                    boss_name = stages[0]["title"]

        context = ToneContext(
            challenge_appetite=challenge_appetite,
            energy_status=state.get("last_energy_status"),
            loot_type=state.get("last_loot_type"),
            boss_name=boss_name,
            stage_label=state.get("onboarding_stage"),
            theme_preference=theme_preference,
            time_of_day=time_of_day,
            loot_title=state.get("last_loot_title"),
            next_progress=state.get("next_progress"),
        )

        return self.coach_responder.generate(
            context,
            now=now or datetime.now(timezone.utc),
        )
