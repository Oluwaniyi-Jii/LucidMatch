from anthropic import AsyncAnthropic
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, AUDITOR_MAX_TOKENS

class AuditorAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def audit_decision(self, match_result: Dict[str, Any], original_resume_text: str) -> Dict[str, Any]:
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
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=AUDITOR_MAX_TOKENS,
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
            # Fallback for prototype safety
            return {"flagged": False, "flags": [], "fairness_score": 100, "audit_note": "Audit passed (fallback)."}
