"""
Shared utilities for AI agents.
Provides common functionality for response parsing and error handling.
"""
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AgentResponseParser:
    """Utility class for parsing AI agent responses"""
    
    @staticmethod
    def extract_json(content: str, fallback: Optional[dict] = None) -> dict:
        """
        Safely extract JSON from LLM response with validation.
        
        Args:
            content: Raw text content from LLM
            fallback: Optional fallback dict if parsing fails
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValueError: If no valid JSON found and no fallback provided
        """
        # First try direct JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parse failed, attempting extraction")
        
        # Fallback to extraction method
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start == -1 or end == 0:
                if fallback is not None:
                    logger.warning("No JSON found in response, using fallback")
                    return fallback
                raise ValueError("No JSON object found in response")
            
            json_str = content[start:end]
            result = json.loads(json_str)
            logger.debug("Successfully extracted JSON from response")
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            if fallback is not None:
                logger.warning(f"JSON extraction failed: {e}, using fallback")
                return fallback
            raise ValueError(f"Failed to parse JSON from response: {e}")
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> bool:
        """
        Validate that response contains all required fields.
        
        Args:
            data: Parsed JSON data
            required_fields: List of required field names
            
        Returns:
            True if all fields present, False otherwise
        """
        missing = [field for field in required_fields if field not in data]
        if missing:
            logger.warning(f"Missing required fields: {missing}")
            return False
        return True
    
    @staticmethod
    def ensure_field(data: dict, field: str, default: Any) -> dict:
        """
        Ensure a field exists in data, adding default if missing.
        
        Args:
            data: Dictionary to check
            field: Field name
            default: Default value if field missing
            
        Returns:
            Updated dictionary
        """
        if field not in data:
            logger.debug(f"Adding missing field '{field}' with default value")
            data[field] = default
        return data
