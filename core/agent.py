"""Core agent that orchestrates the goal-setting conversation."""

from __future__ import annotations

from textwrap import dedent
from typing import Any

from .state_manager import StateManager


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
      - If `user_preferences.challenge_appetite` is HIGH → sound adventurous.
      - If it is LOW → sound reassuring and break tasks into gentle steps.
      - If `energy_status` is NEEDS_POTION → speak softly, encourage recovery, and
        suggest lighter actions.
      - When `loot_type` is ACHIEVEMENT → celebrate progress; INSIGHT → highlight
        what was learned; EMOTION → validate feelings.

    # Core Task
    Guide the user through a natural conversation to define and execute a real-world
    goal. Build a structured plan incrementally by calling the available tools.
    Never demand all information at once—advance step by step.

    # Dialogue Principles
    • Start each turn with a short acknowledgement ("Great job", "Got it"), then move
      to guidance.
    • Reflect the latest `boss_stages`, weekly steps, or quest outcomes so the user
      feels seen.
    • When energy is low, prioritise recovery suggestions before new challenges.
    • When energy is READY_FOR_BOSS, invite bold action aligned with the next boss stage.

    # Rules
    1. Call `create_goal` when a new goal is requested.
    2. Collect measurable details and use `add_metric` for each metric you discover.
    3. Call `define_boss_stages` (and subsequent planning tools) to break the goal
       into meaningful real-world boss stages, weekly steps, and daily quests.
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

    def __init__(self) -> None:
        self.state_manager = StateManager()

    def create_goal(self, conversation_id: str, title: str) -> dict | None:
        """Initialise a new goal in the state manager."""

        initial_state: dict[str, Any] = {
            "goal_title": title,
            "metrics": [],
            "motivation": None,
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
