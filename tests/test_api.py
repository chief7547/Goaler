"""Integration tests for the Flask API layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from api import create_app
from core.storage import SQLAlchemyStorage, create_session_factory


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/api.db"
    monkeypatch.setenv("GOALER_DATABASE_URL", db_url)
    monkeypatch.setenv("GOALER_ACTIVE_USER_ID", "user-1")
    session_factory = create_session_factory(db_url)
    app = create_app(session_factory=session_factory)
    with app.test_client() as client:
        yield client, session_factory


def _seed_sample_data(session_factory) -> dict:
    session = session_factory()
    storage = SQLAlchemyStorage(session)
    goal = storage.create_goal({"title": "API Goal", "user_id": "user-1"})
    storage.create_boss_stage(
        goal["goal_id"],
        {
            "title": "첫 보스",
            "status": "COMPLETED",
            "target_week": 1,
        },
    )
    quest = storage.create_quest(goal["goal_id"], {"title": "러닝 5km"})
    storage.log_quest_event(
        {
            "goal_id": goal["goal_id"],
            "quest_id": quest["quest_id"],
            "outcome": "COMPLETED",
            "occurred_at": datetime(2025, 2, 20, tzinfo=timezone.utc),
            "energy_status": "READY_FOR_BOSS",
            "loot_type": "ACHIEVEMENT",
            "mood_note": "새 기록 달성",
        }
    )
    storage.save_user_preferences(
        {
            "user_id": "user-1",
            "theme_preference": "GAME",
            "challenge_appetite": "MEDIUM",
            "onboarding_stage": "STAGE_1_ENERGY",
        }
    )
    storage.upsert_player_progress(
        {
            "user_id": "user-1",
            "focus_goal_id": goal["goal_id"],
            "stage_label": "STAGE_1_ENERGY",
            "streak_weeks": 2,
        }
    )
    storage.create_reminder(
        {
            "goal_id": goal["goal_id"],
            "channel": "slack",
            "frequency": "daily",
            "preferred_time": "07:30",
        }
    )
    session.close()
    return {"goal": goal, "quest": quest}


def test_goals_endpoint_returns_summary(api_client):
    client, session_factory = api_client
    seeded = _seed_sample_data(session_factory)

    response = client.get("/api/v1/goals")
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert payload[0]["goalId"] == seeded["goal"]["goal_id"]
    assert payload[0]["energyStatus"] == "READY_FOR_BOSS"


def test_goal_detail_endpoint(api_client):
    client, session_factory = api_client
    seeded = _seed_sample_data(session_factory)

    response = client.get(f"/api/v1/goals/{seeded['goal']['goal_id']}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["goalId"] == seeded["goal"]["goal_id"]
    assert payload["bossStages"]
    assert payload["metrics"] == []
    assert payload["reminders"][0]["time"] == "07:30"


def test_chat_flow_and_reminders(api_client):
    client, session_factory = api_client
    seeded = _seed_sample_data(session_factory)

    context_resp = client.get("/api/v1/chat/context")
    assert context_resp.status_code == 200
    session_payload = context_resp.get_json()
    assert session_payload["context"]["goalTitle"] == "API Goal"

    message_resp = client.post("/api/v1/chat/messages", json={"content": "오늘 계획 알려줘"})
    assert message_resp.status_code == 200
    message_payload = message_resp.get_json()
    assert message_payload["messages"][-1]["role"] == "assistant"

    reminders_resp = client.get("/api/v1/reminders")
    assert reminders_resp.status_code == 200
    reminders = reminders_resp.get_json()
    assert reminders[0]["goalId"] == seeded["goal"]["goal_id"]

    update_resp = client.post(
        "/api/v1/reminders",
        json={
            "reminderId": reminders[0]["reminderId"],
            "goalId": seeded["goal"]["goal_id"],
            "channel": "slack",
            "frequency": "weekly",
            "time": "09:00",
            "active": False,
        },
    )
    assert update_resp.status_code == 201
    assert update_resp.get_json()["frequency"] == "weekly"

    test_resp = client.post("/api/v1/reminders/test", json={"channel": "slack"})
    assert test_resp.status_code == 200
    reminder_test = test_resp.get_json()
    assert reminder_test["status"] == "SUCCESS"
    assert "sentAt" in reminder_test


def test_reports_and_quest_logging(api_client):
    client, session_factory = api_client
    seeded = _seed_sample_data(session_factory)

    report_resp = client.get(
        "/api/v1/reports/weekly",
        query_string={"goalId": seeded["goal"]["goal_id"]},
    )
    assert report_resp.status_code == 200
    report = report_resp.get_json()
    assert report["period"] == "weekly"
    assert report["metrics"]

    log_resp = client.post(
        f"/api/v1/quests/{seeded['quest']['quest_id']}/logs",
        json={
            "goalId": seeded["goal"]["goal_id"],
            "outcome": "COMPLETED",
            "energyStatus": "KEEPING_PACE",
            "lootType": "INSIGHT",
            "moodNote": "연락처 010-1234-5678",
        },
    )
    assert log_resp.status_code == 201
    log_payload = log_resp.get_json()
    assert log_payload["lootType"] == "INSIGHT"
    assert "[민감정보]" in log_payload["sanitizedMoodNote"]
