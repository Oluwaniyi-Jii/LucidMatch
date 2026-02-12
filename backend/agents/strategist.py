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
        1. For each gap, suggest a REAL learning resource with an actual URL.
        2. Prioritize well-known platforms: Coursera, Udemy, LinkedIn Learning, YouTube, freeCodeCamp, Codecademy, edX, Pluralsight.
        3. Differentiate between "Quick Win" (1-2 weeks) and "Deep Dive" (1-2 months).
        4. For each resource, provide a direct URL to the course/tutorial/article.
        5. If you're unsure of the exact URL, provide the most likely search URL on that platform.
        
        PLATFORM URL PATTERNS TO USE:
        - Coursera: https://www.coursera.org/search?query=[skill]
        - Udemy: https://www.udemy.com/courses/search/?q=[skill]
        - YouTube: https://www.youtube.com/results?search_query=[skill]+tutorial
        - freeCodeCamp: https://www.freecodecamp.org/learn/
        - LinkedIn Learning: https://www.linkedin.com/learning/search?keywords=[skill]
        - Codecademy: https://www.codecademy.com/search?query=[skill]
        
        OUTPUT FORMAT (JSON):
        {{
            "curriculum": [
                {{
                    "skill": "Gap Name",
                    "resource": "Course/Tutorial Name",
                    "type": "Quick Win or Deep Dive",
                    "estimated_time": "X weeks",
                    "platform": "Platform Name",
                    "url": "https://actual-url-to-resource"
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
