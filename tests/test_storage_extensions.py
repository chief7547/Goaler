"""Additional storage layer behaviour tests for player progress and reminders."""

from datetime import datetime, timezone


def test_save_user_preferences_upserts(storage):
    payload = {
        "user_id": "user-1",
        "challenge_appetite": "HIGH",
        "theme_preference": "PROFESSIONAL",
        "onboarding_stage": "STAGE_1_ENERGY",
    }

    saved = storage.save_user_preferences(payload)
    assert saved["onboarding_stage"] == "STAGE_1_ENERGY"

    payload["challenge_appetite"] = "LOW"
    saved_again = storage.save_user_preferences(payload)
    assert saved_again["challenge_appetite"] == "LOW"


def test_player_progress_upsert_and_get(storage):
    storage.upsert_player_progress(
        {
            "user_id": "user-1",
            "stage_label": "STAGE_1_5_BOSS_PREVIEW",
            "level": 3,
        }
    )

    progress = storage.get_player_progress("user-1")
    assert progress["stage_label"] == "STAGE_1_5_BOSS_PREVIEW"
    assert progress["level"] == 3

    updated = storage.update_player_progress("user-1", {"level": 4})
    assert updated["level"] == 4


def test_reminder_create_and_list_due(storage):
    goal = storage.create_goal({"title": "Reminder Goal", "user_id": "user-rem"})
    due_time = datetime(2025, 2, 20, 10, 0, tzinfo=timezone.utc)
    storage.create_reminder(
        {
            "goal_id": goal["goal_id"],
            "channel": "slack",
            "frequency": "daily",
            "next_run_at": due_time,
            "preferred_time": "10:00",
        }
    )

    results = storage.list_reminders_due(datetime(2025, 2, 21, tzinfo=timezone.utc))
    assert len(results) == 1
    assert results[0]["goal_id"] == goal["goal_id"]
