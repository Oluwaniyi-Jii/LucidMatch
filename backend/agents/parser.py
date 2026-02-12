from anthropic import AsyncAnthropic
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, PARSER_MAX_TOKENS

class ParserAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def parse_resume(self, text: str) -> Dict[str, Any]:
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
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=PARSER_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # reliable json parsing
            content = message.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Parser Error: {e}")
            return {"error": f"Failed to parse resume: {str(e)}"}
