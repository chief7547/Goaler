from core.agent import GoalSettingAgent
from core.storage import InMemoryStorage


def test_create_goal_initialises_state() -> None:
    agent = GoalSettingAgent()
    conv_id = "test_conv_123"

    agent.create_goal(conversation_id=conv_id, title="My Test Goal")

    current_state = agent.state_manager.get_state(conv_id)
    assert current_state is not None
    assert current_state["goal_title"] == "My Test Goal"
    assert "metrics" in current_state
    assert isinstance(current_state["metrics"], list)
    assert current_state["onboarding_stage"] == "STAGE_0_ONBOARDING"
    assert current_state["feature_flags"] == {
        "loot": False,
        "energy": False,
        "boss": False,
    }


def test_add_metric_updates_state() -> None:
    agent = GoalSettingAgent()
    conv_id = "test_conv_123"
    agent.create_goal(conv_id, "My Test Goal")

    agent.add_metric(
        conv_id,
        {
            "metric_name": "Read books",
            "metric_type": "INCREMENTAL",
            "target_value": 10,
            "unit": "books",
        },
    )

    current_state = agent.state_manager.get_state(conv_id)
    assert current_state is not None
    assert len(current_state["metrics"]) == 1
    added_metric = current_state["metrics"][0]
    assert added_metric["metric_name"] == "Read books"
    assert added_metric["target_value"] == 10


def test_set_motivation_updates_state() -> None:
    agent = GoalSettingAgent()
    conv_id = "test_conv_123"
    agent.create_goal(conv_id, "My Test Goal")

    agent.set_motivation(conv_id, "Improve focus")

    current_state = agent.state_manager.get_state(conv_id)
    assert current_state is not None
    assert current_state["motivation"] == "Improve focus"


def test_finalize_goal_clears_state() -> None:
    agent = GoalSettingAgent()
    conv_id = "test_conv_123"
    agent.create_goal(conv_id, "Finalize Test")

    assert agent.state_manager.get_state(conv_id) is not None

    agent.finalize_goal(conv_id)

    assert agent.state_manager.get_state(conv_id) is None


def test_onboarding_context_defaults() -> None:
    agent = GoalSettingAgent()
    conv_id = "ctx_conv"
    agent.create_goal(conv_id, "Context Goal")

    context = agent.get_onboarding_context(conv_id)

    assert context["onboarding_stage"] == "STAGE_0_ONBOARDING"
    assert context["feature_flags"]["loot"] is False
    assert context["feature_flags"]["energy"] is False
    assert context["feature_flags"]["boss"] is False


def test_define_boss_stages_persisted_and_sorted() -> None:
    storage = InMemoryStorage()
    agent = GoalSettingAgent(storage=storage)
    conv_id = "conv_boss"
    goal_id = "goal-123"
    agent.create_goal(conv_id, "Stage Goal")

    response = agent.define_boss_stages(
        conv_id,
        goal_id,
        [
            {
                "title": "사업자등록 완료",
                "description": "홈택스 신청",
                "success_criteria": "등록증 확보",
                "target_week": 6,
            },
            {
                "title": "첫 고객 인터뷰",
                "description": "3건 진행",
                "success_criteria": "인사이트 기록",
                "target_week": 8,
            },
        ],
    )

    assert response["status"] == "ok"
    stored = storage.list_boss_stages(goal_id)
    assert len(stored) == 2
    assert stored[0]["stage_order"] == 1
    assert stored[0]["title"] == "사업자등록 완료"
    state = agent.state_manager.get_state(conv_id)
    assert len(state["boss_stages"]) == 2


def test_propose_weekly_plan_updates_state() -> None:
    storage = InMemoryStorage()
    agent = GoalSettingAgent(storage=storage)
    conv_id = "conv_week"
    goal_id = "goal-456"
    agent.create_goal(conv_id, "Stage Goal")
    boss = agent.define_boss_stages(
        conv_id,
        goal_id,
        [
            {
                "title": "중간 발표",
                "success_criteria": "자료 제출",
            }
        ],
    )["boss_stages"][0]

    weekly_steps = [
        {"title": "자료 초안 정리", "week_index": 1},
        {"title": "피드백 반영", "week_index": 2},
    ]
    result = agent.propose_weekly_plan(conv_id, goal_id, boss["boss_id"], weekly_steps)
    assert result["weekly_plan"] == weekly_steps
    state = agent.state_manager.get_state(conv_id)
    assert state["weekly_plan"][boss["boss_id"]] == weekly_steps


def test_propose_daily_tasks_sets_variations() -> None:
    agent = GoalSettingAgent()
    conv_id = "conv_daily"
    goal_id = "goal-daily"
    agent.create_goal(conv_id, "Daily Goal")

    daily_tasks = [
        {"title": "15분 러닝", "difficulty_tier": "EASY"},
        {"title": "근력 운동", "difficulty_tier": "NORMAL"},
    ]
    weekly_step = {"title": "움직임 익히기"}
    response = agent.propose_daily_tasks(conv_id, goal_id, weekly_step, daily_tasks)
    assert response["daily_tasks"] == daily_tasks
    state = agent.state_manager.get_state(conv_id)
    assert state["current_variations"] == daily_tasks


def test_propose_quests_locked_until_loot_unlocked() -> None:
    agent = GoalSettingAgent()
    conv_id = "conv_variation"
    goal_id = "goal-variation"
    agent.create_goal(conv_id, "Variation Goal")

    result = agent.propose_quests(
        conv_id,
        goal_id,
        [{"title": "집 주변 걷기", "reason": "시동 걸기"}],
    )
    assert result["status"] == "locked"
    assert result["reason"] == "ONBOARDING_STAGE_LOCKED"


def test_propose_quests_after_unlock_returns_variations() -> None:
    agent = GoalSettingAgent()
    conv_id = "conv_variation_unlock"
    goal_id = "goal-variation-unlock"
    agent.create_goal(conv_id, "Variation Goal")
    state = agent.state_manager.get_state(conv_id)
    state["feature_flags"]["loot"] = True
    agent.state_manager.update_state(conv_id, state)

    variations = [
        {"title": "러닝", "difficulty_tier": "NORMAL"},
        {"title": "체중 운동", "difficulty_tier": "EASY"},
    ]
    result = agent.propose_quests(conv_id, goal_id, variations)
    assert result["status"] == "ok"
    assert len(result["variations"]) == 2
    assert result["variations"][0]["reason"] == "기본 추천 변주"


def test_choose_quest_persists_to_storage() -> None:
    storage = InMemoryStorage()
    agent = GoalSettingAgent(storage=storage)
    conv_id = "conv_choose"
    goal_id = "goal-choose"
    agent.create_goal(conv_id, "Choose Goal")
    state = agent.state_manager.get_state(conv_id)
    state["feature_flags"]["loot"] = True
    agent.state_manager.update_state(conv_id, state)

    quest_choice = {
        "title": "러닝 20분",
        "difficulty_tier": "NORMAL",
        "expected_duration_minutes": 20,
        "variation_tags": ["tempo_up"],
    }
    response = agent.choose_quest(conv_id, goal_id, quest_choice)
    assert response["quest"]["title"] == "러닝 20분"


def test_log_quest_outcome_updates_state() -> None:
    storage = InMemoryStorage()
    agent = GoalSettingAgent(storage=storage)
    conv_id = "conv_log"
    goal_id = "goal-log"
    agent.create_goal(conv_id, "Log Goal")

    quest = agent.choose_quest(
        conv_id,
        goal_id,
        {"title": "스트레칭", "difficulty_tier": "EASY"},
    )["quest"]

    log_response = agent.log_quest_outcome(
        conv_id,
        {
            "goal_id": goal_id,
            "quest_id": quest["quest_id"],
            "outcome": "COMPLETED",
            "occurred_at": "2025-02-15T00:00:00",
            "energy_status": "READY_FOR_BOSS",
        },
    )
    assert log_response["log"]["outcome"] == "COMPLETED"
    state = agent.state_manager.get_state(conv_id)
    assert len(state.get("quest_logs", [])) == 1


def test_log_quest_outcome_handles_failure() -> None:
    storage = InMemoryStorage()
    agent = GoalSettingAgent(storage=storage)
    conv_id = "conv_log_fail"
    goal_id = "goal-log-fail"
    agent.create_goal(conv_id, "Log Goal")
    quest = agent.choose_quest(
        conv_id,
        goal_id,
        {"title": "근력 운동", "difficulty_tier": "NORMAL"},
    )["quest"]

    fail_log = agent.log_quest_outcome(
        conv_id,
        {
            "goal_id": goal_id,
            "quest_id": quest["quest_id"],
            "outcome": "FAILED",
            "occurred_at": "2025-02-15T00:00:00",
            "energy_status": "NEEDS_POTION",
            "perceived_difficulty": "TOO_HARD",
            "loot_type": "EMOTION",
        },
    )

    assert fail_log["log"]["outcome"] == "FAILED"
    state = agent.state_manager.get_state(conv_id)
    assert state["quest_logs"][-1]["energy_status"] == "NEEDS_POTION"
