"""
Agent 4: Tool Decision Agent
Decides whether to call the database write tool based on validation status.
"""

from typing import Dict, Any
from prompts import AGENT_4_TOOL_DECISION_PROMPT_TEMPLATE


class ToolDecisionAgent:
    """Decides whether to execute database write tool."""
    
    def __init__(self):
        self.prompt_template = AGENT_4_TOOL_DECISION_PROMPT_TEMPLATE
    
    def decide(self, validation_result: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide whether to call database write tool.
        
        Args:
            validation_result: Result from validation agent
            extracted_data: Extracted invoice data
            
        Returns:
            Dictionary with decision and action
        """
        status = validation_result.get("status", "incomplete")
        
        if status == "valid":
            return {
                "should_write": True,
                "reason": "Invoice validation passed",
                "data_to_write": extracted_data
            }
        else:
            return {
                "should_write": False,
                "reason": f"Validation failed: {', '.join(validation_result.get('errors', []))}",
                "data_to_write": None
            }
