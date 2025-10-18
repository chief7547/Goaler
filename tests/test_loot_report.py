import json
from datetime import datetime, timezone
from tools.generate_loot_report import gather_summary, render_report, write_report
from core.storage import SQLAlchemyStorage, create_session


def _build_storage():
    session = create_session("sqlite:///:memory:")
    return SQLAlchemyStorage(session)


def test_gather_summary_produces_counts(tmp_path):
    storage = _build_storage()
    goal = storage.create_goal({"title": "신제품 출시", "user_id": "user-1"})
    storage.create_boss_stage(
        goal["goal_id"],
        {
            "title": "시장 조사",
            "status": "COMPLETED",
        },
    )
    quest = storage.create_quest(
        goal["goal_id"],
        {"title": "고객 인터뷰", "variation_tags": ["insight"]},
    )
    storage.log_quest_event(
        {
            "goal_id": goal["goal_id"],
            "quest_id": quest["quest_id"],
            "outcome": "COMPLETED",
            "occurred_at": datetime(2025, 2, 10, tzinfo=timezone.utc),
            "loot_type": "ACHIEVEMENT",
            "energy_status": "READY_FOR_BOSS",
            "mood_note": "시장 피드백 정리",
        }
    )

    usage_log = tmp_path / "llm_usage.log"
    usage_log.write_text(
        json.dumps(
            {
                "timestamp": "2025-02-09T09:00:00",
                "model": "gpt-5",
                "prompt_tokens": 10,
                "completion_tokens": 5,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary = gather_summary(
        storage,
        period="monthly",
        user_id="user-1",
        now=datetime(2025, 2, 15, tzinfo=timezone.utc),
        usage_log=usage_log,
    )

    assert summary["loot_counts"]["ACHIEVEMENT"] == 1
    assert summary["boss_completed"] == ["시장 조사"]
    assert summary["usage_summary"]["total_requests"] == 1

    content = render_report(summary)
    assert "시장 피드백 정리" in content
    assert "시장 조사" in content

    output = write_report(content, summary, tmp_path)
    assert output.exists()
    written = output.read_text(encoding="utf-8")
    assert "user-1" in output.name
    assert "전리품" in written
