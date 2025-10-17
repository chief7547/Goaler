"""Lightweight function schemas presented to the LLM tooling interface."""


def create_goal(title: str) -> None:
    """Schema stub for the `create_goal` tool."""


def add_metric(
    metric_name: str,
    target_value: float,
    unit: str,
    metric_type: str = "INCREMENTAL",
    initial_value: float | None = None,
) -> None:
    """Schema stub for the `add_metric` tool."""


def set_motivation(text: str) -> None:
    """Schema stub for the `set_motivation` tool."""


def finalize_goal() -> None:
    """Schema stub for the `finalize_goal` tool."""


def define_boss_stages(goal_id: str, boss_candidates: list[dict]) -> None:
    """Schema stub for the `define_boss_stages` tool."""


def propose_weekly_plan(goal_id: str, boss_id: str, weekly_plan: list[dict]) -> None:
    """Schema stub for the `propose_weekly_plan` tool."""


def propose_daily_tasks(goal_id: str, weekly_step: dict, daily_tasks: list[dict]) -> None:
    """Schema stub for the `propose_daily_tasks` tool."""


def propose_quests(goal_id: str, candidate_pool: list[dict]) -> None:
    """Schema stub for the `propose_quests` tool."""


def choose_quest(goal_id: str, quest_choice: dict) -> None:
    """Schema stub for the `choose_quest` tool."""


def log_quest_outcome(goal_id: str, quest_id: str, outcome: str) -> None:
    """Schema stub for the `log_quest_outcome` tool."""
