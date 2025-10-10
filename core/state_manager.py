"""
This module defines the StateManager, which is responsible for holding and 
managing the state of a goal-setting conversation.
"""

# For a real implementation, this would use a more robust key-value store like Redis.
# For this prototype, a simple Python dictionary is sufficient to demonstrate the logic.
_STATE_CACHE = {}

class StateManager:
    """Manages the in-progress goal object for each conversation."""

    def new_conversation(self, conversation_id: str, initial_state: dict):
        """Starts a new conversation with an initial state."""
        print(f"--- STATE: New conversation started: {conversation_id} ---")
        _STATE_CACHE[conversation_id] = initial_state
        return True

    def get_state(self, conversation_id: str) -> dict | None:
        """Retrieves the current state for a given conversation."""
        return _STATE_CACHE.get(conversation_id)

    def update_state(self, conversation_id: str, new_state: dict):
        """Updates the state for a given conversation."""
        if conversation_id not in _STATE_CACHE:
            return False
        print(f"--- STATE: State updated for {conversation_id} ---")
        _STATE_CACHE[conversation_id].update(new_state)
        return True

    def end_conversation(self, conversation_id: str):
        """Clears the state for a finished or expired conversation."""
        if conversation_id in _STATE_CACHE:
            print(f"--- STATE: Conversation ended: {conversation_id} ---")
            del _STATE_CACHE[conversation_id]
        return True

# --- Example Usage (for demonstration) ---

if __name__ == '__main__':
    conv_id = "user123_session456"
    state_manager = StateManager()

    # 1. A new conversation starts
    state_manager.new_conversation(conv_id, {"goal_title": "Learn Python"})
    print("Current state:", state_manager.get_state(conv_id))

    # 2. A metric is added during the conversation
    current_goal = state_manager.get_state(conv_id)
    if 'metrics' not in current_goal:
        current_goal['metrics'] = []
    current_goal['metrics'].append({
        "metric_name": "Complete exercises",
        "metric_type": "INCREMENTAL",
        "target_value": 50,
        "unit": "exercises"
    })
    state_manager.update_state(conv_id, current_goal)
    print("Updated state:", state_manager.get_state(conv_id))

    # 3. The conversation ends
    state_manager.end_conversation(conv_id)
    print("Final state:", state_manager.get_state(conv_id))
