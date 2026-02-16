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
        import re
        
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
            
            # Clean up common JSON formatting issues
            # Remove trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            # Fix missing commas between array elements (common AI mistake)
            json_str = re.sub(r'}(\s*){', r'},\1{', json_str)
            # Fix missing commas after string values before next key
            json_str = re.sub(r'"(\s*)"([a-zA-Z_])', r'",\1"\2', json_str)
            
            # Try parsing the cleaned JSON
            try:
                result = json.loads(json_str)
                logger.debug("Successfully extracted JSON from response")
                return result
            except json.JSONDecodeError as parse_error:
                # Try aggressive repairs
                logger.warning(f"First parse failed at char {parse_error.pos}, attempting JSON repair")
                try:
                    fixed_str = json_str
                    # Additional fix: ensure proper comma placement
                    fixed_str = re.sub(r'}\s*{', r'},{', fixed_str)
                    # Fix incomplete final element - if the JSON ends abruptly
                    if not fixed_str.rstrip().endswith(']}') and not fixed_str.rstrip().endswith('}}'):
                        # Try to close incomplete structures
                        if '"curriculum":' in fixed_str:
                            # Count open/close brackets
                            open_brackets = fixed_str.count('[')
                            close_brackets = fixed_str.count(']')
                            open_braces = fixed_str.count('{')
                            close_braces = fixed_str.count('}')
                            
                            # Add missing closing characters
                            if open_brackets > close_brackets:
                                fixed_str += ']' * (open_brackets - close_brackets)
                            if open_braces > close_braces:
                                fixed_str += '}' * (open_braces - close_braces)
                    
                    result = json.loads(fixed_str)
                    logger.info("Successfully repaired and parsed JSON")
                    return result
                except json.JSONDecodeError as final_error:
                    # Log the problematic section for debugging
                    logger.error(f"JSON repair failed. Error at position {final_error.pos}")
                    if final_error.pos < len(json_str):
                        context_start = max(0, final_error.pos - 100)
                        context_end = min(len(json_str), final_error.pos + 100)
                        logger.error(f"Context around error: ...{json_str[context_start:context_end]}...")
                    # Raise the original error
                    raise parse_error
            
        except (json.JSONDecodeError, ValueError) as e:
            # Log the error for debugging
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Content preview: {content[:500]}...")
            
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
