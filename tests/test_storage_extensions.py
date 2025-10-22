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


def test_create_metric_and_list(storage):
    goal = storage.create_goal({"title": "Metric Goal", "user_id": "metric-user"})
    storage.create_metric(
        goal["goal_id"],
        {
            "metric_name": "주간 러닝",
            "metric_type": "INCREMENTAL",
            "target_value": 3,
            "unit": "회",
        },
    )

    metrics = storage.list_metrics(goal["goal_id"])
    assert len(metrics) == 1
    assert metrics[0]["metric_name"] == "주간 러닝"


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


def test_conversation_log_roundtrip(storage):
    goal = storage.create_goal({"title": "Conversation Goal", "user_id": "log-user"})
    log = storage.create_conversation_log(
        {
            "conversation_id": "conv-1",
            "goal_id": goal["goal_id"],
            "role": "assistant",
            "content": "안녕하세요",
            "token_count": 12,
        }
    )
    assert log["role"] == "assistant"

    fetched = storage.list_conversation_logs("conv-1")
    assert len(fetched) == 1
    assert fetched[0]["content"] == "안녕하세요"


def test_mood_note_sanitized(storage):
    goal = storage.create_goal({"title": "Privacy Goal", "user_id": "privacy"})
    quest = storage.create_quest(goal["goal_id"], {"title": "테스트"})
    log = storage.log_quest_event(
        {
            "goal_id": goal["goal_id"],
            "quest_id": quest["quest_id"],
            "outcome": "COMPLETED",
            "occurred_at": datetime(2025, 2, 10, tzinfo=timezone.utc),
            "mood_note": "이메일 test@example.com 과 전화 010-1234-5678",
        }
    )
    assert "[민감정보]" in log["mood_note"]
    assert "test@example.com" not in log["mood_note"]
