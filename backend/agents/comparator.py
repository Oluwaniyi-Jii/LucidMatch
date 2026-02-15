from anthropic import AsyncAnthropic
import json
import logging
from typing import Dict, Any

from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, COMPARATOR_MAX_TOKENS
from exceptions import ComparatorError
from utils.agent_utils import AgentResponseParser

logger = logging.getLogger(__name__)


class ComparatorAgent:
    """Agent responsible for comparing two candidates head-to-head"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.parser = AgentResponseParser()

    async def compare_candidates(self, profile_a: Dict[str, Any], profile_b: Dict[str, Any], job_context: str) -> Dict[str, Any]:
        """
        Compare two candidates for a specific role.
        
        Args:
            profile_a: First candidate's profile
            profile_b: Second candidate's profile
            job_context: Job description and requirements
            
        Returns:
            Comparison results with advantages and verdict
            
        Raises:
            ComparatorError: If comparison fails
        """
        prompt = f"""
        You are the Comparator Agent. Your goal is to provide a "Head-to-Head" analysis of two candidates for a specific role.
        
        JOB CONTEXT:
        {job_context}
        
        CANDIDATE A:
        {json.dumps(profile_a, indent=2)}
        
        CANDIDATE B:
        {json.dumps(profile_b, indent=2)}
        
        TASK:
        1. Compare them directly on key job requirements.
        2. Identify the "Winning Edge" for each (why choose A? why choose B?).
        3. Provide a final relative recommendation.
        
        OUTPUT FORMAT (JSON):
        {{
            "advantage_a": ["Stronger leadership...", "Better Python skills..."],
            "advantage_b": ["More years of experience...", "Cheaper salary expectation (inferred)..."],
            "verdict": "Candidate A is preferred because despite having less experience, their specific stack overlap is perfect...",
            "comparison_points": [
                {{"dimension": "Technical Skills", "winner": "A", "reason": "A has React, B does not."}},
                {{"dimension": "Soft Skills", "winner": "B", "reason": "B demonstrates more mentorship."}}
            ]
        }}
        """

        try:
            logger.info("Calling Comparator Agent")
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=COMPARATOR_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            result = self.parser.extract_json(content)
            
            logger.info("Comparator Agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Comparator Agent failed: {e}", exc_info=True)
            raise ComparatorError(f"Failed to compare candidates: {str(e)}")
