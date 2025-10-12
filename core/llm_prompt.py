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
