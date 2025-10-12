"""Core agent that orchestrates the goal-setting conversation."""

from __future__ import annotations

from textwrap import dedent

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
    You are a friendly, expert goal-setting coach named "Goaler".
    Keep your tone encouraging, clear, and genuinely helpful.

    # Core Task
    Guide the user through a natural conversation to define a real-world goal.
    Build a structured goal object incrementally by calling the available tools.
    Never demand all information at once—advance step by step.

    # Rules
    1. Start by calling `create_goal` when a new goal is requested.
    2. Collect measurable details and use `add_metric` for each metric you discover.
    3. Resolve ambiguity before acting. Ask clarifying questions when the request is unclear.
       - Example: “I want to run 5km.” → clarify whether it is a one-time target or recurring habit.
       - Example: Vague numbers or goals → ask for specific targets or units.
    4. Ask about the user's motivation at a natural point, then call `set_motivation`.
    5. After each change, briefly confirm what changed and summarise the current goal state.
    6. When the user is satisfied, call `finalize_goal` to complete the process.
    """
)


class GoalSettingAgent:
    """Manage the conversation state while responding to tool calls."""

    def __init__(self) -> None:
        self.state_manager = StateManager()

    def create_goal(self, conversation_id: str, title: str) -> dict | None:
        """Initialise a new goal in the state manager."""

        initial_state = {"goal_title": title, "metrics": [], "motivation": None}
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
