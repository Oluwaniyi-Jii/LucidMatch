from anthropic import AsyncAnthropic
import logging
from typing import Dict, Any

from config import ANTHROPIC_API_KEY, HAIKU_MODEL, PARSER_MAX_TOKENS
from exceptions import ParserError
from utils.agent_utils import AgentResponseParser

logger = logging.getLogger(__name__)


class ParserAgent:
    """Agent responsible for parsing resumes and extracting structured information"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.parser = AgentResponseParser()

    async def parse_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract competency clusters.
        
        Args:
            text: Raw resume text
            
        Returns:
            Structured profile data
            
        Raises:
            ParserError: If parsing fails
        """
        prompt = f"""
        You are an expert HR Parser Agent. Your goal is to extract skills and experience from a resume and structure them into "Competency Clusters".
        
        RULES:
        1. Identify technical skills, soft skills, and domain expertise.
        2. Group them into logical clusters (e.g., "Data Analysis", "Project Management").
        3. Assign a proficiency level (Beginner, Intermediate, Advanced, Expert) implementation based on context.
        4. STRIP ALL PII (Personal Identifiable Information). Do not include names, emails, phone numbers, or addresses.
        5. Return ONLY valid JSON.
        
        RESUME TEXT:
        {text}
        
        OUTPUT FORMAT (JSON):
        {{
            "competency_clusters": {{
                "Cluster Name": ["Skill 1", "Skill 2"]
            }},
            "experience_level": "Junior/Mid/Senior",
            "years_of_experience": estimated_number
        }}
        """

        try:
            logger.info("Calling Parser Agent")
            message = await self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=PARSER_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            result = self.parser.extract_json(content)
            
            logger.info("Parser Agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Parser Agent failed: {e}", exc_info=True)
            raise ParserError(f"Failed to parse resume: {str(e)}")
