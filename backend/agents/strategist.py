from anthropic import AsyncAnthropic
import json
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, STRATEGIST_MAX_TOKENS

class StrategistAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def generate_curriculum(self, skill_gaps: List[str]) -> Dict[str, Any]:
        prompt = f"""
        You are the Strategist Agent. Your goal is to recommend a "Bridge Curriculum" to close the identified skill gaps.
        
        SKILL GAPS:
        {json.dumps(skill_gaps)}
        
        TASK:
        1. For each gap, suggest a learning resource (Course, Article, Project).
        2. Differentiate between "Quick Wins" (1-2 weeks) and "Deep Dives" (1-2 months).
        3. Ensure resources are real or realistic types (e.g., "Coursera: Advanced SQL").
        
        OUTPUT FORMAT (JSON):
        {{
            "curriculum": [
                {{
                    "skill": "Gap Name",
                    "resource": "Course Name/Platform",
                    "type": "Quick Win/Deep Dive",
                    "estimated_time": "X weeks"
                }}
            ],
            "estimated_total_time": "X months"
        }}
        """

        try:
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=STRATEGIST_MAX_TOKENS,
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
            return {"curriculum": [], "error": str(e)}
