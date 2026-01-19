"""
Database Tool
Mock implementation of database write tool for demonstration.
In production, this would connect to a real database.
"""

from typing import Dict, Any
import json
from datetime import datetime


class DatabaseTool:
    """Tool for writing validated invoices to database."""
    
    def __init__(self, db_path: str = "invoices_db.json"):
        """
        Initialize database tool.
        
        Args:
            db_path: Path to JSON file (mock database)
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def write_invoice_to_db(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write validated invoice to database.
        
        Args:
            invoice_data: Validated invoice data
            
        Returns:
            Dictionary with write result
        """
        try:
            # Load existing invoices
            invoices = self._load_invoices()
            
            # Add metadata
            invoice_record = {
                **invoice_data,
                "id": len(invoices) + 1,
                "created_at": datetime.now().isoformat(),
                "status": "stored"
            }
            
            # Add to database
            invoices.append(invoice_record)
            
            # Save to file
            self._save_invoices(invoices)
            
            return {
                "success": True,
                "message": "Invoice successfully written to database",
                "invoice_id": invoice_record["id"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing to database: {str(e)}",
                "invoice_id": None
            }
    
    def _ensure_db_exists(self):
        """Ensure database file exists."""
        import os
        if not os.path.exists(self.db_path):
            self._save_invoices([])
    
    def _load_invoices(self) -> list:
        """Load invoices from database file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    
    def _save_invoices(self, invoices: list):
        """Save invoices to database file."""
        with open(self.db_path, 'w') as f:
            json.dump(invoices, f, indent=2)
