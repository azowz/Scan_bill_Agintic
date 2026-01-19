"""
Master Orchestrator
Coordinates all agents in the invoice processing pipeline.
"""

from typing import Dict, Any, Optional
from agents.document_ingestion_agent import DocumentIngestionAgent
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.tool_decision_agent import ToolDecisionAgent
from tools.database_tool import DatabaseTool
from prompts import SYSTEM_PROMPT


class InvoiceProcessingOrchestrator:
    """Orchestrates the entire invoice processing workflow."""
    
    def __init__(self, openrouter_api_key: Optional[str] = None, 
                 model: Optional[str] = None, use_easyocr: bool = False):
        """
        Initialize orchestrator with all agents.
        
        Args:
            openrouter_api_key: OpenRouter API key for extraction agent
            model: Model to use (default: openai/gpt-4o for Arabic, or from env)
            use_easyocr: Use EasyOCR instead of Tesseract (better for low-quality images)
        """
        self.document_agent = DocumentIngestionAgent(use_easyocr=use_easyocr)
        self.extraction_agent = ExtractionAgent(api_key=openrouter_api_key, model=model)
        self.validation_agent = ValidationAgent()
        self.tool_decision_agent = ToolDecisionAgent()
        self.database_tool = DatabaseTool()
        
        self.system_prompt = SYSTEM_PROMPT
    
    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Process invoice through the entire pipeline.
        
        Args:
            file_path: Path to invoice file (PDF or image)
            
        Returns:
            Dictionary with all pipeline steps and results
        """
        pipeline_results = {
            "system_prompt": self.system_prompt,
            "steps": {}
        }
        
        try:
            # Step 1: Document Ingestion
            pipeline_results["steps"]["document_ingestion"] = {
                "agent": "Document Ingestion Agent",
                "status": "processing",
                "input": {"file_path": file_path},
                "output": None
            }
            
            ingestion_result = self.document_agent.process(file_path)
            pipeline_results["steps"]["document_ingestion"]["output"] = ingestion_result
            pipeline_results["steps"]["document_ingestion"]["status"] = "success"
            
            raw_text = ingestion_result.get("raw_text", "")
            
            if not raw_text.strip():
                pipeline_results["steps"]["document_ingestion"]["status"] = "error"
                pipeline_results["steps"]["document_ingestion"]["error"] = "No text extracted from document"
                return pipeline_results
            
            # Step 2: Information Extraction
            pipeline_results["steps"]["extraction"] = {
                "agent": "Information Extraction Agent",
                "status": "processing",
                "input": {"raw_text_length": len(raw_text)},
                "output": None
            }
            
            extracted_data = self.extraction_agent.extract(raw_text)
            pipeline_results["steps"]["extraction"]["output"] = extracted_data
            pipeline_results["steps"]["extraction"]["status"] = "success"
            
            # Step 3: Validation
            pipeline_results["steps"]["validation"] = {
                "agent": "Validation Agent",
                "status": "processing",
                "input": extracted_data,
                "output": None
            }
            
            validation_result = self.validation_agent.validate(extracted_data)
            pipeline_results["steps"]["validation"]["output"] = validation_result
            pipeline_results["steps"]["validation"]["status"] = "success" if validation_result["status"] == "valid" else "failed"
            
            # Step 4: Tool Decision
            pipeline_results["steps"]["tool_decision"] = {
                "agent": "Tool Decision Agent",
                "status": "processing",
                "input": {
                    "validation_status": validation_result["status"],
                    "extracted_data": extracted_data
                },
                "output": None
            }
            
            decision_result = self.tool_decision_agent.decide(validation_result, extracted_data)
            pipeline_results["steps"]["tool_decision"]["output"] = decision_result
            pipeline_results["steps"]["tool_decision"]["status"] = "success"
            
            # Step 5: Database Write (if decision is to write)
            if decision_result.get("should_write", False):
                pipeline_results["steps"]["database_write"] = {
                    "agent": "Database Tool",
                    "status": "processing",
                    "input": decision_result["data_to_write"],
                    "output": None
                }
                
                db_result = self.database_tool.write_invoice_to_db(decision_result["data_to_write"])
                pipeline_results["steps"]["database_write"]["output"] = db_result
                pipeline_results["steps"]["database_write"]["status"] = "success" if db_result.get("success") else "error"
            else:
                pipeline_results["steps"]["database_write"] = {
                    "agent": "Database Tool",
                    "status": "skipped",
                    "reason": decision_result.get("reason", "Validation failed"),
                    "output": None
                }
            
            pipeline_results["overall_status"] = "success" if validation_result["status"] == "valid" else "incomplete"
            
        except Exception as e:
            pipeline_results["overall_status"] = "error"
            pipeline_results["error"] = str(e)
        
        return pipeline_results
