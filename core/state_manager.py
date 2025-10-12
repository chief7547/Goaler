"""Manage in-memory conversation state for the goal-setting agent."""

# For a production system we would use a persistent store (Redis, database, etc.).
# The simple dictionary is enough for this prototype and keeps tests lightweight.
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
        state = _STATE_CACHE.get(conversation_id)
        return state.copy() if state else None

    def update_state(self, conversation_id: str, new_state: dict):
        """Updates the state for a given conversation."""
        if conversation_id not in _STATE_CACHE:
            return False
        print(f"--- STATE: State updated for {conversation_id} ---")
        _STATE_CACHE[conversation_id] = new_state
        return True

    def end_conversation(self, conversation_id: str):
        """Clears the state for a finished or expired conversation."""
        if conversation_id in _STATE_CACHE:
            print(f"--- STATE: Conversation ended: {conversation_id} ---")
            del _STATE_CACHE[conversation_id]
        return True


# --- Example Usage (for demonstration) ---

if __name__ == "__main__":
    conv_id = "user123_session456"
    state_manager = StateManager()

    state_manager.new_conversation(conv_id, {"goal_title": "Learn Python"})
    print("Current state:", state_manager.get_state(conv_id))

    current_goal = state_manager.get_state(conv_id)
    if current_goal is not None:
        current_goal.setdefault("metrics", []).append(
            {
                "metric_name": "Complete exercises",
                "metric_type": "INCREMENTAL",
                "target_value": 50,
                "unit": "exercises",
            }
        )
        state_manager.update_state(conv_id, current_goal)
        print("Updated state:", state_manager.get_state(conv_id))

    state_manager.end_conversation(conv_id)
    print("Final state:", state_manager.get_state(conv_id))
