"""
This module defines the pure function specifications (schemas) for the LLM tools.
These functions are for schema generation only and do not contain implementation logic.
The GoalSettingAgent contains the actual implementation.
"""

# By defining the functions here without implementation, we provide a clean schema to the LLM.
# The LLM only needs to know about the arguments it can extract from the user's text.

def create_goal(title: str):
    """
    Creates a new goal. This should be the first step.
    
    Args:
        title (str): A short, descriptive title for the goal (e.g., "Learn Python", "Read 10 books").
    """
    pass

def add_metric(metric_name: str, target_value: float, unit: str, metric_type: str = "INCREMENTAL", initial_value: float = 0):
    """
    Adds a new measurable metric to the current goal.
    
    Args:
        metric_name (str): The name of the metric (e.g., "Weight", "Books read").
        target_value (float): The target value to achieve.
        unit (str): The unit of measurement (e.g., "kg", "books").
        metric_type (str, optional): The type of metric. Defaults to "INCREMENTAL".
        initial_value (float, optional): The starting value, if applicable. Defaults to 0.
    """
    pass

def set_motivation(text: str):
    """
    Sets the user's motivation or "epic meaning" for the goal.
    
    Args:
        text (str): The user's description of why they want to achieve the goal.
    """
    pass

def finalize_goal():
    """
    Finalizes the goal-setting process.
    """
    pass