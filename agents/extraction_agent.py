"""
Agent 2: Information Extraction Agent (LLM Core)
Extracts structured invoice fields from raw text using semantic understanding.
Uses OpenRouter API for LLM access.
"""

import json
from typing import Dict, Any, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

from prompts import AGENT_2_EXTRACTION_PROMPT_TEMPLATE

load_dotenv()


class ExtractionAgent:
    """Extracts invoice fields semantically from raw text.
    
    Uses OpenRouter API for LLM access.
    Optimized for Arabic invoices using GPT-4o for best Arabic understanding.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize extraction agent.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: openai/gpt-4o for Arabic, or openai/gpt-4o-mini for cost-effective)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables. Get your key from https://openrouter.ai")
        
        # Use GPT-4o for Arabic invoices (best choice), or allow override
        # OpenRouter model format: openai/gpt-4o or just gpt-4o
        default_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
        self.model = model or default_model
        
        # Initialize OpenRouter client with custom base URL
        # OpenRouter uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.prompt_template = AGENT_2_EXTRACTION_PROMPT_TEMPLATE
    
    def extract(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract invoice fields from raw text.
        
        Args:
            raw_text: Raw text extracted from invoice
            
        Returns:
            Dictionary with extracted invoice fields
        """
        # Use safe replacement instead of .format() to avoid issues with curly braces 
        # in the prompt template (JSON schema) or input text
        prompt = self.prompt_template.replace("{raw_text}", raw_text)
        
        try:
            # OpenRouter supports OpenAI-compatible API
            # Models can be: openai/gpt-4o, openai/gpt-4o-mini, anthropic/claude-3-opus, etc.
            response = self.client.chat.completions.create(
                model=self.model,  # openai/gpt-4o for Arabic invoices (best), or openai/gpt-4o-mini for cost-effective
                messages=[
                    {"role": "system", "content": "You are a precise JSON extraction agent specialized in Arabic and multilingual invoices. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,  # Limit output tokens to save cost and avoid error 402
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            extracted_data = json.loads(result_text)
            
            return extracted_data
            
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            try:
                result_text = response.choices[0].message.content
                return self._parse_json_from_text(result_text)
            except:
                return {
                    "biller_name": None,
                    "biller_address": None,
                    "total_amount": None,
                    "due_date": None,
                    "error": "Failed to parse JSON response"
                }
        except Exception as e:
            # Fallback to cheaper model if 402 or other error occurs
            if "402" in str(e) or "credits" in str(e).lower():
                try:
                    print("⚠️ Switching to gpt-4o-mini due to credit limit...")
                    response = self.client.chat.completions.create(
                        model="openai/gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a precise JSON extraction agent. Return only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=1000,
                        response_format={"type": "json_object"}
                    )
                    result_text = response.choices[0].message.content
                    return json.loads(result_text)
                except Exception as ex:
                     return {
                        "biller_name": None,
                        "biller_address": None,
                        "total_amount": None,
                        "due_date": None,
                        "error": f"Fallback failed: {str(ex)}"
                    }
            
            return {
                "biller_name": None,
                "biller_address": None,
                "total_amount": None,
                "due_date": None,
                "error": str(e)
            }
    
    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        """Try to extract JSON from text response."""
        try:
            # Look for JSON block
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "biller_name": None,
            "biller_address": None,
            "total_amount": None,
            "due_date": None,
            "error": "Failed to parse JSON"
        }
