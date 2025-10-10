import pytest
from core.agent import GoalSettingAgent

def test_create_goal_initializes_state():
    """
    Tests if agent.create_goal correctly initializes a new conversation state.
    """
    conv_id = "test_conv_123"
    goal_title = "My Test Goal"
    
    # 1. Create the agent
    agent = GoalSettingAgent()
    
    # 2. Call the agent's method
    agent.create_goal(conversation_id=conv_id, title=goal_title)
    
    # 3. Verify the state through the agent's state_manager
    current_state = agent.state_manager.get_state(conv_id)
    
    assert current_state is not None
    assert current_state["goal_title"] == goal_title
    assert "metrics" in current_state
    assert isinstance(current_state["metrics"], list)

def test_add_metric_updates_state():
    """
    Tests if agent.add_metric correctly adds a new metric to the goal state.
    """
    conv_id = "test_conv_123"
    goal_title = "My Test Goal"
    
    # 1. Create the agent and initialize a goal
    agent = GoalSettingAgent()
    agent.create_goal(conv_id, goal_title)
    
    # 2. Call the (not-yet-implemented) add_metric method
    metric_details = {
        "metric_name": "Read books",
        "metric_type": "INCREMENTAL",
        "target_value": 10,
        "unit": "books"
    }
    agent.add_metric(conv_id, metric_details)
    
    # 3. Verify that the state has been updated
    current_state = agent.state_manager.get_state(conv_id)
    assert len(current_state["metrics"]) == 1
    added_metric = current_state["metrics"][0]
    assert added_metric["metric_name"] == "Read books"
    assert added_metric["target_value"] == 10

def test_set_motivation_updates_state():
    """
    Tests if agent.set_motivation correctly updates the motivation in the goal state.
    """
    conv_id = "test_conv_123"
    goal_title = "My Test Goal"
    motivation_text = "I want to be a better version of myself."
    
    # 1. Create the agent and initialize a goal
    agent = GoalSettingAgent()
    agent.create_goal(conv_id, goal_title)
    
    # 2. Call the (not-yet-implemented) set_motivation method
    agent.set_motivation(conv_id, motivation_text)
    
    # 3. Verify that the state has been updated
    current_state = agent.state_manager.get_state(conv_id)
    assert current_state["motivation"] == motivation_text

def test_finalize_goal_clears_state():
    """
    Tests if agent.finalize_goal correctly clears the conversation state.
    """
    conv_id = "test_conv_123"
    
    # 1. Create the agent and initialize a goal
    agent = GoalSettingAgent()
    agent.create_goal(conv_id, "Finalize Test")
    
    # Verify state exists before finalizing
    assert agent.state_manager.get_state(conv_id) is not None
    
    # 2. Call the (not-yet-implemented) finalize_goal method
    agent.finalize_goal(conv_id)
    
    # 3. Verify that the state has been cleared
    assert agent.state_manager.get_state(conv_id) is None
