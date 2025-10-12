from core.agent import GoalSettingAgent


def test_create_goal_initialises_state() -> None:
    agent = GoalSettingAgent()
    conv_id = "test_conv_123"

    agent.create_goal(conversation_id=conv_id, title="My Test Goal")

    current_state = agent.state_manager.get_state(conv_id)
    assert current_state is not None
    assert current_state["goal_title"] == "My Test Goal"
    assert "metrics" in current_state
    assert isinstance(current_state["metrics"], list)


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
