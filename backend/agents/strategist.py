<<<<<<< HEAD
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
=======
"""
Strategist Agent - Upskilling Curriculum Generation

The Strategist Agent builds personalized learning paths:
1. Identifies skill gaps from the Reasoner's output
2. Prioritizes "Quick Wins" (1-2 weeks) vs "Core Learning" (1-2 months)
3. Recommends real, validated learning resources
4. Estimates total upskilling time
"""

import json
import re
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI

from config import get_settings, Settings
from schemas import (
    SkillGap,
    UpskillPath,
    LearningResource,
    GapPriority
)


# Pre-validated learning resources (prevents hallucination)
LEARNING_LIBRARY = {
    "python": [
        {"title": "Python for Everybody", "provider": "Coursera", "url": "https://www.coursera.org/specializations/python", "duration_hours": 40},
        {"title": "Complete Python Bootcamp", "provider": "Udemy", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "duration_hours": 22}
    ],
    "sql": [
        {"title": "SQL for Data Science", "provider": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science", "duration_hours": 15},
        {"title": "The Complete SQL Bootcamp", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "duration_hours": 9}
    ],
    "data analysis": [
        {"title": "Google Data Analytics", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "duration_hours": 180},
        {"title": "Data Analysis with Python", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "duration_hours": 300}
    ],
    "project management": [
        {"title": "Google Project Management", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-project-management", "duration_hours": 160},
        {"title": "PMP Certification Prep", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/paths/prepare-for-the-pmp-certification", "duration_hours": 35}
    ],
    "agile": [
        {"title": "Agile with Atlassian Jira", "provider": "Coursera", "url": "https://www.coursera.org/learn/agile-atlassian-jira", "duration_hours": 12},
        {"title": "Scrum Master Certification", "provider": "Scrum.org", "url": "https://www.scrum.org/professional-scrum-master-i-certification", "duration_hours": 20}
    ],
    "excel": [
        {"title": "Excel Skills for Business", "provider": "Coursera", "url": "https://www.coursera.org/specializations/excel", "duration_hours": 60},
        {"title": "Excel Essential Training", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/excel-essential-training-microsoft-365", "duration_hours": 5}
    ],
    "tableau": [
        {"title": "Data Visualization with Tableau", "provider": "Coursera", "url": "https://www.coursera.org/specializations/data-visualization", "duration_hours": 80},
        {"title": "Tableau Essential Training", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/tableau-essential-training-14959992", "duration_hours": 6}
    ],
    "aws": [
        {"title": "AWS Cloud Practitioner Essentials", "provider": "AWS", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "duration_hours": 6},
        {"title": "AWS Solutions Architect", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/aws-cloud-solutions-architect", "duration_hours": 120}
    ],
    "machine learning": [
        {"title": "Machine Learning by Andrew Ng", "provider": "Coursera", "url": "https://www.coursera.org/learn/machine-learning", "duration_hours": 60},
        {"title": "Deep Learning Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning", "duration_hours": 160}
    ],
    "user research": [
        {"title": "User Research and Design", "provider": "Coursera", "url": "https://www.coursera.org/learn/user-research", "duration_hours": 20},
        {"title": "UX Research Methods", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/ux-research-methods", "duration_hours": 4}
    ],
    "figma": [
        {"title": "Introduction to Figma", "provider": "Figma", "url": "https://www.figma.com/resources/learn-design/", "duration_hours": 10},
        {"title": "Figma UI/UX Design Essentials", "provider": "Udemy", "url": "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/", "duration_hours": 14}
    ],
    "javascript": [
        {"title": "JavaScript Algorithms and Data Structures", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "duration_hours": 300},
        {"title": "The Complete JavaScript Course", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "duration_hours": 69}
    ],
    "react": [
        {"title": "React - The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "duration_hours": 50},
        {"title": "Front-End Development with React", "provider": "Coursera", "url": "https://www.coursera.org/learn/front-end-react", "duration_hours": 45}
    ],
    "communication": [
        {"title": "Business Communication", "provider": "Coursera", "url": "https://www.coursera.org/specializations/business-english", "duration_hours": 40},
        {"title": "Communication Skills for Leaders", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/communication-skills-for-leaders", "duration_hours": 3}
    ],
    "leadership": [
        {"title": "Leading People and Teams", "provider": "Coursera", "url": "https://www.coursera.org/specializations/leading-teams", "duration_hours": 60},
        {"title": "Leadership Foundations", "provider": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/leadership-foundations-4", "duration_hours": 2}
    ]
}


class StrategistAgent:
    """
    Generates personalized upskilling paths based on identified skill gaps.
    Recommends validated, real-world learning resources.
    """
    
    SYSTEM_PROMPT = """You are an expert learning strategist who creates personalized upskilling paths.

Given a list of skill gaps, you must:
1. Prioritize skills by importance and learning time
2. Identify "Quick Wins" - skills learnable in 1-2 weeks
3. Plan "Core Learning" - deeper skills requiring 1-2 months
4. Suggest a logical learning sequence

PRIORITIZATION RULES:
- Critical gaps come first (blocking factors for the role)
- Quick wins boost confidence and demonstrate progress
- Build foundational skills before advanced ones
- Consider skill dependencies (SQL before advanced data analysis)

OUTPUT FORMAT (JSON):
{
    "quick_wins": [
        {"skill": "Excel", "learning_time_weeks": 1, "reason": "Immediate productivity boost"}
    ],
    "core_learning": [
        {"skill": "SQL", "learning_time_weeks": 4, "reason": "Foundation for data work"}
    ],
    "priority_order": ["Excel", "SQL", "Tableau"],
    "total_time_weeks": 6,
    "learning_strategy": "Start with Excel for quick wins, then build SQL foundation..."
}"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate AI client"""
        if self.settings.ai_provider == "anthropic":
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            self.provider = "anthropic"
        elif self.settings.ai_provider == "openai":
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.provider = "openai"
        else:
            self.client = None
            self.provider = "none"

    async def generate_curriculum(self, skill_gaps: list[SkillGap]) -> UpskillPath:
        """
        Generate a personalized learning curriculum based on skill gaps.
        
        Args:
            skill_gaps: List of identified skill gaps from the Reasoner
        
        Returns:
            UpskillPath with prioritized learning resources
        """
        if not skill_gaps:
            return UpskillPath(
                quick_wins=[],
                core_learning=[],
                total_time_weeks=0,
                priority_order=[]
            )
        
        # For Phase 1, use a deterministic approach with pre-validated resources
        # This prevents hallucination and ensures real courses
        return self._build_curriculum_from_library(skill_gaps)
    
    def _build_curriculum_from_library(self, gaps: list[SkillGap]) -> UpskillPath:
        """Build curriculum using validated learning library"""
        quick_wins = []
        core_learning = []
        priority_order = []
        total_weeks = 0
        
        # Sort by priority
        sorted_gaps = sorted(gaps, key=lambda g: (
            0 if g.priority == GapPriority.CRITICAL else 
            1 if g.priority == GapPriority.IMPORTANT else 2
        ))
        
        for gap in sorted_gaps:
            skill_lower = gap.skill.lower()
            priority_order.append(gap.skill)
            
            # Find matching resources in library
            resources = None
            for key, value in LEARNING_LIBRARY.items():
                if key in skill_lower or skill_lower in key:
                    resources = value
                    break
            
            if resources:
                # Pick first (primary) resource
                res = resources[0]
                learning_resource = LearningResource(
                    title=res["title"],
                    provider=res["provider"],
                    url=res.get("url"),
                    duration_hours=res.get("duration_hours"),
                    skill_addressed=gap.skill
                )
                
                # Quick win if learning time <= 2 weeks (assume 10 hrs/week)
                hours = res.get("duration_hours", 40)
                weeks = hours / 10
                total_weeks += weeks
                
                if weeks <= 2:
                    quick_wins.append(learning_resource)
                else:
                    core_learning.append(learning_resource)
            else:
                # Generic recommendation for unlisted skills
                if gap.learning_time_weeks and gap.learning_time_weeks <= 2:
                    quick_wins.append(LearningResource(
                        title=f"{gap.skill} Fundamentals",
                        provider="LinkedIn Learning",
                        skill_addressed=gap.skill,
                        duration_hours=10
                    ))
                    total_weeks += gap.learning_time_weeks
                else:
                    core_learning.append(LearningResource(
                        title=f"{gap.skill} Complete Course",
                        provider="Coursera/Udemy",
                        skill_addressed=gap.skill,
                        duration_hours=40
                    ))
                    total_weeks += gap.learning_time_weeks or 4
        
        return UpskillPath(
            quick_wins=quick_wins,
            core_learning=core_learning,
            total_time_weeks=int(total_weeks),
            priority_order=priority_order
        )
    
    def _find_resource(self, skill: str) -> Optional[dict]:
        """Find a learning resource for a given skill"""
        skill_lower = skill.lower()
        for key, resources in LEARNING_LIBRARY.items():
            if key in skill_lower or skill_lower in key:
                return resources[0]
        return None
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
