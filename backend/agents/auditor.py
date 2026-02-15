from anthropic import AsyncAnthropic
import json
import logging
from typing import Dict, Any

from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, AUDITOR_MAX_TOKENS
from exceptions import AuditorError
from utils.agent_utils import AgentResponseParser
from constants import AgentDefaults

logger = logging.getLogger(__name__)


class AuditorAgent:
    """Agent responsible for auditing matching decisions for bias"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.parser = AgentResponseParser()

    async def audit_decision(self, match_result: Dict[str, Any], original_resume_text: str) -> Dict[str, Any]:
        """
        Audit a matching decision for potential bias.
        
        Args:
            match_result: The matching result to audit
            original_resume_text: Original resume text for context
            
        Returns:
            Audit results with bias flags and scores
            
        Raises:
            AuditorError: If audit fails
        """
        prompt = f"""
        You are the Auditor Agent. Your job is to review the recruitment matching decision for BIAS.
        
        MATCH RESULT:
        {json.dumps(match_result, indent=2)}
        
        ORIGINAL RESUME SNIPPET:
        {original_resume_text[:1000]}...
        
        CHECKS:
        1. Socioeconomic Proxies: Are there mentions of expensive hobbies (sailing, polo) or specific universities?
        2. Gender/Demographic Bias: Does the reasoning rely on gendered keywords?
        3. Ageism: Are there flags for "digital native" or "seasoned veteran"?
        
        OUTPUT FORMAT (JSON):
        {{
            "flagged": true/false,
            "flags": ["Flag description 1"],
            "fairness_score": 0-100,
            "social_bias_score": 0-100,
            "gender_bias_score": 0-100,
            "age_bias_score": 0-100,
            "audit_note": "Clear explanation of findings."
        }}
        """

        try:
            logger.info("Calling Auditor Agent")
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=AUDITOR_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            result = self.parser.extract_json(content)
            
            # Ensure required fields exist
            result = self.parser.ensure_field(result, "flagged", False)
            result = self.parser.ensure_field(result, "flags", [])
            result = self.parser.ensure_field(result, "fairness_score", AgentDefaults.FALLBACK_FAIRNESS_SCORE)
            result = self.parser.ensure_field(result, "audit_note", "Audit completed")
            
            logger.info(f"Auditor Agent completed: flagged={result['flagged']}")
            return result
            
        except Exception as e:
            logger.error(f"Auditor Agent failed: {e}", exc_info=True)
            raise AuditorError(f"Failed to audit decision: {str(e)}")
