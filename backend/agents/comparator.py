from anthropic import AsyncAnthropic
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, COMPARATOR_MAX_TOKENS

class ComparatorAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def compare_candidates(self, profile_a: Dict[str, Any], profile_b: Dict[str, Any], job_context: str) -> Dict[str, Any]:
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
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=COMPARATOR_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Comparator Error: {e}")
            return {"error": "Failed to compare candidates"}
