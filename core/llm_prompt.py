"""
This module defines the core prompt and function specifications for the LLM agent
that handles the conversational goal-setting process.
"""

# --- System Prompt for the Goal-Setting Agent ---

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

# --- Function (Tool) Definitions for the LLM ---
# Note: These are the function signatures the LLM will be trained to call.
# The actual implementation will be in a different module.

def create_goal(title: str):
    """
    Creates a new goal object in the conversation state. This is the first step.
    
    Args:
        title (str): A short, descriptive title for the goal.
    """
    print(f"--- TOOL CALL: create_goal(title='{title}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def add_metric(metric_name: str, metric_type: str, target_value: float, unit: str, initial_value: float = None):
    """
    Adds a new measurable metric to the current goal.
    
    Args:
        metric_name (str): The name of the metric (e.g., "Weight", "Running Distance").
        metric_type (str): The type of metric. Supported types: 'INCREMENTAL', 'DECREMENTAL'.
        target_value (float): The target value to achieve.
        unit (str): The unit of measurement (e.g., "kg", "km", "pages").
        initial_value (float, optional): The starting value, if applicable.
    """
    print(f"--- TOOL CALL: add_metric(name='{metric_name}', type='{metric_type}', target={target_value}, unit='{unit}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def set_motivation(text: str):
    """
    Sets the user's motivation or "epic meaning" for the goal.
    
    Args:
        text (str): The user's description of why they want to achieve the goal.
    """
    print(f"--- TOOL CALL: set_motivation(text='{text}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def finalize_goal():
    """
    Finalizes the goal-setting process and saves the goal to the database.
    """
    print("--- TOOL CALL: finalize_goal() ---")
    # In a real implementation, this would move the goal from the StateManager to the permanent DB.
    pass
