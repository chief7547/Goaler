"""User preference and context loading utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserPreferences:
    challenge_appetite: str = "MEDIUM"
    theme_preference: str = "GAME"
    onboarding_stage: str = "STAGE_0_ONBOARDING"


class ContextLoader:
    """Interface for loading user preference context attributes."""

    def __init__(self, storage):
        self.storage = storage

    def get_user_preferences(self, user_id: str) -> UserPreferences:
        record = self.storage.get_user_preferences(user_id)
        if not record:
            return UserPreferences()
        return UserPreferences(
            challenge_appetite=record.get("challenge_appetite", "MEDIUM"),
            theme_preference=record.get("theme_preference", "GAME"),
            onboarding_stage=record.get("onboarding_stage", "STAGE_0_ONBOARDING"),
        )


__all__ = ["UserPreferences", "ContextLoader"]
