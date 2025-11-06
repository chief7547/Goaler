"""Flask API surface that exposes Goaler data for the frontend."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from flask import Flask, abort, current_app, g, jsonify, request

from core.agent import GoalSettingAgent, STAGE_0
from core.storage import SQLAlchemyStorage, create_session_factory
from tools.generate_loot_report import gather_summary


def create_app(*, session_factory=None) -> Flask:
    app = Flask(__name__)
    app.config["SESSION_FACTORY"] = session_factory or create_session_factory()

    @app.teardown_appcontext
    def _teardown(_exc: BaseException | None) -> None:
        session = g.pop("db_session", None)
        if session is not None:
            session.close()

    @app.get("/api/v1/goals")
    def list_goals() -> Any:
        storage = _get_storage()
        user_id = _active_user_id()
        status = request.args.get("status")
        goals = storage.list_goals(user_id=user_id, status=status)
        prefs = storage.get_user_preferences(user_id) or {}
        summaries = [
            _serialize_goal_summary(storage, goal, user_id, prefs)
            for goal in goals
        ]
        return jsonify(summaries)

    @app.get("/api/v1/goals/<goal_id>")
    def get_goal_detail(goal_id: str) -> Any:
        storage = _get_storage()
        user_id = _active_user_id()
        goal = storage.get_goal(goal_id)
        if not goal or goal["user_id"] != user_id:
            abort(404, description="Goal not found")
        prefs = storage.get_user_preferences(user_id) or {}
        detail = _serialize_goal_detail(storage, goal, user_id, prefs)
        return jsonify(detail)

    @app.post("/api/v1/quests/<quest_id>/logs")
    def log_quest(quest_id: str) -> Any:
        payload = request.get_json(silent=True) or {}
        goal_id = payload.get("goalId")
        outcome = payload.get("outcome")
        if not goal_id or not outcome:
            abort(400, description="goalId and outcome are required")
        storage = _get_storage()
        user_id = _active_user_id()
        goal = storage.get_goal(goal_id)
        if not goal or goal["user_id"] != user_id:
            abort(404, description="Goal not found")
        log = storage.log_quest_event(
            {
                "goal_id": goal_id,
                "quest_id": quest_id,
                "outcome": outcome,
                "occurred_at": payload.get("occurredAt") or datetime.now(timezone.utc),
                "energy_status": payload.get("energyStatus"),
                "loot_type": payload.get("lootType"),
                "mood_note": payload.get("moodNote"),
                "perceived_difficulty": payload.get("perceivedDifficulty"),
            }
        )
        return jsonify(_serialize_loot_entry(log)), 201

    @app.get("/api/v1/reminders")
    def list_reminders() -> Any:
        storage = _get_storage()
        user_id = _active_user_id()
        reminders = storage.list_reminders(user_id=user_id)
        response = [_serialize_reminder(reminder) for reminder in reminders]
        return jsonify(response)

    @app.post("/api/v1/reminders")
    def upsert_reminder() -> Any:
        payload = request.get_json(silent=True) or {}
        goal_id = payload.get("goalId")
        if not goal_id:
            abort(400, description="goalId is required")
        storage = _get_storage()
        user_id = _active_user_id()
        goal = storage.get_goal(goal_id)
        if not goal or goal["user_id"] != user_id:
            abort(404, description="Goal not found")
        reminder_id = payload.get("reminderId")
        preferred_time = payload.get("time")
        if reminder_id:
            reminder = storage.update_reminder(
                reminder_id,
                {
                    "channel": payload.get("channel"),
                    "frequency": payload.get("frequency"),
                    "active": payload.get("active"),
                    "preferred_time": preferred_time,
                },
            )
            if reminder is None:
                abort(404, description="Reminder not found")
        else:
            reminder = storage.create_reminder(
                {
                    "goal_id": goal_id,
                    "channel": payload.get("channel", "slack"),
                    "frequency": payload.get("frequency", "daily"),
                    "preferred_time": preferred_time,
                    "active": payload.get("active", True),
                }
            )
        return jsonify(_serialize_reminder(reminder)), 201

    @app.post("/api/v1/reminders/test")
    def test_reminder() -> Any:
        payload = request.get_json(silent=True) or {}
        _ = payload  # payload accepted for compatibility
        sent_at = datetime.now(timezone.utc).isoformat()
        return jsonify({"status": "SUCCESS", "sentAt": sent_at})

    @app.get("/api/v1/reports/<period>")
    def get_report(period: str) -> Any:
        if period not in {"weekly", "monthly"}:
            abort(400, description="Unsupported period")
        storage = _get_storage()
        user_id = _active_user_id()
        goal_id = request.args.get("goalId")
        summary = gather_summary(
            storage,
            period=period,
            user_id=user_id,
            goal_id=goal_id,
        )
        response = _serialize_report(summary, period)
        return jsonify(response)

    @app.get("/api/v1/chat/context")
    def chat_context() -> Any:
        storage = _get_storage()
        agent = _build_agent(storage)
        user_id = _active_user_id()
        session = _build_chat_session(storage, agent, user_id)
        return jsonify(session)

    @app.post("/api/v1/chat/messages")
    def chat_message() -> Any:
        payload = request.get_json(silent=True) or {}
        content = payload.get("content")
        if not content:
            abort(400, description="content is required")
        storage = _get_storage()
        agent = _build_agent(storage)
        user_id = _active_user_id()
        conversation_id = _conversation_id(user_id)
        focus_goal = _get_focus_goal(storage, user_id)
        if focus_goal is None:
            abort(400, description="Goal is required before starting chat")
        _ensure_conversation_state(agent, focus_goal, user_id)
        storage.create_conversation_log(
            {
                "conversation_id": conversation_id,
                "goal_id": focus_goal["goal_id"],
                "role": "user",
                "content": content,
            }
        )
        reply = agent.compose_coach_reply(conversation_id)
        storage.create_conversation_log(
            {
                "conversation_id": conversation_id,
                "goal_id": focus_goal["goal_id"],
                "role": "assistant",
                "content": reply,
            }
        )
        session = _build_chat_session(storage, agent, user_id)
        return jsonify(session)

    return app


def _get_storage() -> SQLAlchemyStorage:
    if "storage" not in g:
        session_factory = current_app.config["SESSION_FACTORY"]
        session = session_factory()
        g.db_session = session
        g.storage = SQLAlchemyStorage(session)
    return g.storage


def _build_agent(storage: SQLAlchemyStorage) -> GoalSettingAgent:
    return GoalSettingAgent(storage=storage)


def _active_user_id() -> str:
    user_id = os.getenv("GOALER_ACTIVE_USER_ID")
    if not user_id:
        raise RuntimeError("GOALER_ACTIVE_USER_ID must be configured")
    return user_id


def _serialize_goal_summary(
    storage: SQLAlchemyStorage,
    goal: dict,
    user_id: str,
    prefs: dict,
) -> dict[str, Any]:
    stage_label = _resolve_stage_label(storage, user_id)
    boss_stages = storage.list_boss_stages(goal["goal_id"])
    completed_steps = sum(1 for stage in boss_stages if stage.get("status") == "COMPLETED")
    total_steps = max(len(boss_stages), 1)
    recent_logs = storage.list_recent_quest_logs(goal["goal_id"], limit=1)
    energy_status = "KEEPING_PACE"
    if recent_logs:
        energy_status = recent_logs[0].get("energy_status") or energy_status
    quests = storage.list_quests(goal["goal_id"])
    next_action = None
    if quests:
        quest = quests[0]
        next_action = {
            "questId": quest["quest_id"],
            "title": quest["title"],
            "due": None,
        }
    theme_preference = prefs.get("theme_preference", "GAME")
    return {
        "goalId": goal["goal_id"],
        "title": goal["title"],
        "stage": stage_label,
        "progress": {
            "completedSteps": completed_steps,
            "totalSteps": total_steps,
        },
        "energyStatus": energy_status or "KEEPING_PACE",
        "nextAction": next_action,
        "themePreference": theme_preference,
    }


def _serialize_goal_detail(
    storage: SQLAlchemyStorage,
    goal: dict,
    user_id: str,
    prefs: dict,
) -> dict[str, Any]:
    summary = _serialize_goal_summary(storage, goal, user_id, prefs)
    boss_stages = storage.list_boss_stages(goal["goal_id"])
    metrics = storage.list_metrics(goal["goal_id"])
    quest_logs = storage.list_recent_quest_logs(goal["goal_id"], limit=50)
    reminders = storage.list_reminders(goal_id=goal["goal_id"])
    detail = {
        **summary,
        "motivation": goal.get("motivation") or "",
        "bossStages": [_serialize_boss_stage(stage) for stage in boss_stages],
        "metrics": [_serialize_metric(metric) for metric in metrics],
        "lootLog": [_serialize_loot_entry(log) for log in quest_logs],
        "reminders": [_serialize_reminder(reminder) for reminder in reminders],
    }
    return detail


def _serialize_boss_stage(stage: dict) -> dict[str, Any]:
    return {
        "bossId": stage["boss_id"],
        "title": stage["title"],
        "status": stage.get("status", "PLANNED"),
        "targetWeek": stage.get("target_week") or 0,
        "weeklyPlan": [],
        "dailyTasks": [],
    }


def _serialize_metric(metric: dict) -> dict[str, Any]:
    current_value = (
        metric.get("progress")
        if metric.get("progress") is not None
        else metric.get("initial_value")
    )
    if current_value is None:
        current_value = 0
    return {
        "metricId": metric["metric_id"],
        "name": metric["metric_name"],
        "unit": metric.get("unit") or "",
        "targetValue": metric.get("target_value") or 0,
        "currentValue": current_value,
    }


def _serialize_loot_entry(log: dict) -> dict[str, Any]:
    return {
        "logId": log["log_id"],
        "questId": log.get("quest_id"),
        "goalId": log.get("goal_id"),
        "outcome": log.get("outcome"),
        "sanitizedMoodNote": log.get("mood_note"),
        "energyStatus": log.get("energy_status") or "KEEPING_PACE",
        "lootType": log.get("loot_type") or "ACHIEVEMENT",
        "createdAt": log.get("occurred_at") or log.get("created_at"),
    }


def _serialize_reminder(reminder: dict) -> dict[str, Any]:
    return {
        "reminderId": reminder["reminder_id"],
        "goalId": reminder["goal_id"],
        "channel": reminder.get("channel", "slack"),
        "frequency": reminder.get("frequency", "daily"),
        "time": reminder.get("preferred_time") or "09:00",
        "timezone": os.getenv("GOALER_DEFAULT_TIMEZONE", "UTC"),
        "active": reminder.get("active", True),
        "lastSentAt": reminder.get("next_run_at"),
    }


def _serialize_report(summary: dict, period: str) -> dict[str, Any]:
    loot_counts = summary.get("loot_counts", {})
    energy_counts = summary.get("energy_counts", {})
    highlights = []
    if summary.get("boss_completed"):
        highlights.append(
            {
                "id": "completed",
                "title": "보스전 완료",
                "description": ", ".join(summary["boss_completed"]),
                "fx": "quest_complete",
            }
        )
    if summary.get("boss_in_progress"):
        highlights.append(
            {
                "id": "progress",
                "title": "진행 중인 보스",
                "description": ", ".join(summary["boss_in_progress"]),
                "fx": "stage_upgrade",
            }
        )
    if summary.get("boss_next"):
        highlights.append(
            {
                "id": "upcoming",
                "title": "다음 목표",
                "description": ", ".join(summary["boss_next"]),
                "fx": "energy_warning",
            }
        )

    metric_values = []
    for label in ["ACHIEVEMENT", "INSIGHT", "EMOTION"]:
        metric_values.append({"label": label, "value": loot_counts.get(label, 0)})

    metrics = [
        {
            "metricId": "loot",
            "name": "전리품 횟수",
            "unit": "회",
            "values": metric_values,
        },
        {
            "metricId": "energy",
            "name": "에너지 상태 기록",
            "unit": "회",
            "values": [
                {"label": key, "value": energy_counts.get(key, 0)}
                for key in ["READY_FOR_BOSS", "KEEPING_PACE", "NEEDS_POTION"]
            ],
        },
    ]

    story_entries = []
    for idx, quote in enumerate(summary.get("recent_quotes", []), start=1):
        story_entries.append({"heading": f"메모 {idx}", "body": quote})
    if not story_entries:
        story_entries.append(
            {
                "heading": "요약",
                "body": "최근 기간 동안 기록된 전리품이 없습니다."
            }
        )

    return {
        "period": period,
        "highlights": highlights,
        "metrics": metrics,
        "story": story_entries,
    }


def _build_chat_session(
    storage: SQLAlchemyStorage,
    agent: GoalSettingAgent,
    user_id: str,
) -> dict[str, Any]:
    focus_goal = _get_focus_goal(storage, user_id)
    if focus_goal is None:
        return {
            "messages": [],
            "context": {
                "goalTitle": "",
                "stageLabel": STAGE_0,
                "energyStatus": "KEEPING_PACE",
                "streakCount": 0,
                "recentLoot": [],
            },
        }
    _ensure_conversation_state(agent, focus_goal, user_id)
    conversation_id = _conversation_id(user_id)
    logs = list(reversed(storage.list_conversation_logs(conversation_id, limit=50)))
    messages = [
        {
            "messageId": log["log_id"],
            "role": log.get("role", "assistant"),
            "content": log.get("content", ""),
            "createdAt": log.get("created_at"),
            "suggestions": [],
        }
        for log in logs
    ]
    progress = storage.get_player_progress(user_id) or {}
    stage_label = progress.get("stage_label", STAGE_0)
    quest_logs = storage.list_recent_quest_logs(focus_goal["goal_id"], limit=5)
    recent_loot = [
        {
            "type": log.get("loot_type") or "ACHIEVEMENT",
            "label": log.get("mood_note") or "기록됨",
        }
        for log in quest_logs
        if log.get("loot_type")
    ]
    latest_energy = "KEEPING_PACE"
    if quest_logs:
        latest_energy = quest_logs[0].get("energy_status") or latest_energy
    context = {
        "goalTitle": focus_goal.get("title", ""),
        "stageLabel": stage_label,
        "energyStatus": latest_energy,
        "streakCount": progress.get("streak_weeks", 0) or 0,
        "recentLoot": recent_loot,
    }
    return {"messages": messages, "context": context}


def _ensure_conversation_state(
    agent: GoalSettingAgent,
    focus_goal: dict,
    user_id: str,
) -> None:
    conversation_id = _conversation_id(user_id)
    state = agent.state_manager.get_state(conversation_id)
    if state is None:
        agent.state_manager.new_conversation(
            conversation_id,
            {
                "user_id": user_id,
                "goal_id": focus_goal["goal_id"],
                "goal_title": focus_goal.get("title"),
                "motivation": focus_goal.get("motivation"),
                "onboarding_stage": _resolve_stage_label(agent.storage, user_id),
            },
        )


def _resolve_stage_label(storage: SQLAlchemyStorage, user_id: str) -> str:
    progress = storage.get_player_progress(user_id)
    if progress and progress.get("stage_label"):
        return progress["stage_label"]
    return STAGE_0


def _get_focus_goal(storage: SQLAlchemyStorage, user_id: str) -> dict | None:
    progress = storage.get_player_progress(user_id)
    if progress and progress.get("focus_goal_id"):
        goal = storage.get_goal(progress["focus_goal_id"])
        if goal:
            return goal
    goals = storage.list_goals(user_id=user_id)
    return goals[0] if goals else None


def _conversation_id(user_id: str) -> str:
    return f"chat_api_{user_id}"


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
