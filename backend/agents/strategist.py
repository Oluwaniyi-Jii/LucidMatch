from anthropic import AsyncAnthropic
import json
import logging
from typing import Dict, Any, List

from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, STRATEGIST_MAX_TOKENS
from exceptions import StrategistError
from utils.agent_utils import AgentResponseParser

logger = logging.getLogger(__name__)


class StrategistAgent:
    """Agent responsible for generating upskilling curricula"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.parser = AgentResponseParser()

    async def generate_curriculum(self, skill_gaps: List[str]) -> Dict[str, Any]:
        """
        Generate upskilling curriculum for identified skill gaps.
        
        Args:
            skill_gaps: List of skills to address
            
        Returns:
            Curriculum with learning resources
            
        Raises:
            StrategistError: If curriculum generation fails
        """
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
            logger.info(f"Calling Strategist Agent for {len(skill_gaps)} skill gaps")
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=STRATEGIST_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            result = self.parser.extract_json(content)
            
            # Ensure curriculum field exists
            result = self.parser.ensure_field(result, "curriculum", [])
            
            logger.info(f"Strategist Agent completed with {len(result.get('curriculum', []))} recommendations")
            return result
            
        except Exception as e:
            logger.error(f"Strategist Agent failed: {e}", exc_info=True)
            raise StrategistError(f"Failed to generate curriculum: {str(e)}")
