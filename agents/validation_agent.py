"""
Agent 3: Validation Agent
Validates extracted invoice fields according to business rules.
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from dateutil import parser

from prompts import AGENT_3_VALIDATION_PROMPT_TEMPLATE


class ValidationAgent:
    """Validates extracted invoice data."""
    
    def __init__(self):
        self.prompt_template = AGENT_3_VALIDATION_PROMPT_TEMPLATE
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted invoice fields.
        
        Args:
            extracted_data: Dictionary with extracted invoice fields
            
        Returns:
            Dictionary with validation status and errors
        """
        errors = []
        
        # Check required fields (Relaxed address requirement)
        required_fields = ["biller_name", "total_amount"]
        for field in required_fields:
            if field not in extracted_data or extracted_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate total_amount
        if "total_amount" in extracted_data and extracted_data["total_amount"] is not None:
            try:
                amount = float(extracted_data["total_amount"])
                if amount <= 0:
                    errors.append("total_amount must be a positive number")
            except (ValueError, TypeError):
                errors.append("total_amount must be a valid number")
        
        # Validate due_date
        if "due_date" in extracted_data and extracted_data["due_date"] is not None:
            if not self._is_valid_date(extracted_data["due_date"]):
                errors.append("due_date must be a valid date format")
        
        # Return validation result
        if len(errors) == 0:
            return {
                "status": "valid",
                "errors": []
            }
        else:
            return {
                "status": "incomplete",
                "errors": errors
            }
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is valid."""
        try:
            # Try parsing the date
            parsed_date = parser.parse(date_str)
            return True
        except (ValueError, TypeError):
            return False
