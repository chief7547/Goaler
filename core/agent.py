"""
This module contains the GoalSettingAgent, which orchestrates the entire
conversational goal-setting process.
"""

from .state_manager import StateManager

class GoalSettingAgent:
    """
    The agent that manages the conversation and interacts with the LLM tools.
    """
    def __init__(self):
        self.state_manager = StateManager()

    def create_goal(self, conversation_id: str, title: str):
        """
        Creates a new goal, initializing it in the state manager.
        """
        initial_state = {
            "goal_title": title,
            "metrics": [],
            "motivation": None
        }
        self.state_manager.new_conversation(conversation_id, initial_state)
        return self.state_manager.get_state(conversation_id)

    def add_metric(self, conversation_id: str, metric_details: dict):
        """
        Adds a new metric to the current goal state.
        """
        current_state = self.state_manager.get_state(conversation_id)
        if not current_state:
            return None
        
        current_state["metrics"].append(metric_details)
        
        self.state_manager.update_state(conversation_id, current_state)
        return current_state

    def set_motivation(self, conversation_id: str, text: str):
        """
        Sets the motivation for the current goal.
        """
        current_state = self.state_manager.get_state(conversation_id)
        if not current_state:
            return None
        
        # This is the line that was missing.
        current_state["motivation"] = text
        
        self.state_manager.update_state(conversation_id, current_state)
        return current_state

    def finalize_goal(self, conversation_id: str):
        """
        Finalizes the goal, saves it to a permanent store (future work),
        and clears the conversation state.
        """
        final_state = self.state_manager.get_state(conversation_id)
        
        # TODO: Add logic here to save the final_state to a permanent database.
        print(f"--- DB: Saving final state for {conversation_id} to database: {final_state} ---")
        
        self.state_manager.end_conversation(conversation_id)
        return True