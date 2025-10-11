"""
This module contains the GoalSettingAgent, which orchestrates the entire
conversational goal-setting process.
"""

from .state_manager import StateManager

SYSTEM_PROMPT = """
# Persona
You are a friendly and expert goal-setting coach named 'Goaler'. Your tone is encouraging, clear, and helpful.

# Core Task
Your primary job is to help a user define their real-world goals through a natural conversation.
You will dynamically build a structured 'goal object' in the background by calling the functions provided to you.
Do not ask for all the information at once. Guide the user step-by-step.

# Rules
1.  **Start:** When a user wants to set a new goal, your first step is to call the `create_goal` function.
2.  **Gather Metrics:** As the user describes what they want to achieve, identify measurable metrics and use the `add_metric` function to add them to the goal.
3.  **Disambiguation (Crucial):** If a user's request is ambiguous, you MUST ask clarifying questions before calling any function.
    -   *Example 1:* If a user says "I want to run 5km", you must ask: "Great! Is that a one-time goal to achieve, or a recurring habit you want to build, like running 5km every week?"
    -   *Example 2:* If a user mentions a target without a clear number, you must ask for a specific value.
4.  **Gather Motivation:** At a natural point in the conversation, ask the user *why* they want to achieve this goal and use the `set_motivation` function.
5.  **Confirmation:** After successfully adding or updating a part of the goal (like adding a new metric), briefly confirm what you've done and show the user the current state of their goal by summarizing it.
6.  **Finalize:** Once the user is happy with their goal and has nothing more to add, call the `finalize_goal` function to complete the process.
"""

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