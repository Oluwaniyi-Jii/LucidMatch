"""
Parser Agent - Skill Extraction & PII Anonymization

The Parser Agent reads raw resume text and:
1. Strips PII (names, contact info, demographics) for blind evaluation
2. Extracts skills and groups them into competency clusters
3. Identifies experience level, education, and achievements
4. Returns structured JSON for the Reasoner agent
"""

import json
import re
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI

from config import get_settings, Settings
from schemas import (
    ParsedProfile, 
    Skill, 
    ProficiencyLevel,
    CompetencyCluster
)


class ParserAgent:
    """
    Extracts and structures candidate information from raw resume text.
    Implements PII stripping for bias-free evaluation.
    """
    
    SYSTEM_PROMPT = """You are an expert resume parser for an AI-driven talent matching system.
Your job is to extract skills, experience, and qualifications from resume text.

CRITICAL PRIVACY REQUIREMENTS:
- NEVER include names, email addresses, phone numbers, or physical addresses
- NEVER include age, gender, or demographic information
- NEVER include specific company names (use industry descriptors instead, e.g., "Fortune 500 tech company")
- NEVER include university names (use level descriptors, e.g., "Top 50 CS program" or just "Bachelor's degree")
- Focus ONLY on skills, competencies, achievements, and transferable abilities

SKILL EXTRACTION RULES:
1. Identify both explicit skills (listed) and implicit skills (demonstrated through experience)
2. Group related skills into competency clusters
3. Assess proficiency level based on context:
   - beginner: Mentioned once, no depth shown
   - intermediate: Used in projects, 1-3 years
   - advanced: Led projects, 3-5 years, significant achievements
   - expert: Industry recognition, 5+ years, teaching/mentoring others

COMPETENCY CLUSTER CATEGORIES:
- technical_programming: Programming languages, frameworks
- data_analysis: SQL, Excel, visualization, statistics
- cloud_infrastructure: AWS, Azure, GCP, DevOps
- project_management: Agile, Scrum, leadership
- communication: Writing, presenting, stakeholder management
- domain_expertise: Industry-specific knowledge
- soft_skills: Problem-solving, collaboration, adaptability

OUTPUT FORMAT (JSON):
{
    "competency_clusters": {
        "cluster_name": ["skill1", "skill2"]
    },
    "skills": [
        {"name": "skill", "proficiency": "intermediate", "years_experience": 2, "context": "how used"}
    ],
    "experience_years": 5.0,
    "experience_level": "intermediate",
    "education_level": "Bachelor's",
    "certifications": ["cert1", "cert2"],
    "achievements": ["quantified achievement 1", "quantified achievement 2"],
    "industries": ["Technology", "Finance"],
    "confidence_score": 0.85
}

CONFIDENCE SCORING:
- 0.9-1.0: Rich detail, clear progression, quantified achievements
- 0.7-0.9: Good detail, some gaps in timeline or specifics
- 0.5-0.7: Sparse information, unclear experience levels
- Below 0.5: Very limited information, may need more data"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate AI client based on configuration"""
        if self.settings.ai_provider == "anthropic":
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            self.provider = "anthropic"
        elif self.settings.ai_provider == "openai":
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.provider = "openai"
        else:
            self.client = None
            self.provider = "none"
    
    def _strip_pii_regex(self, text: str) -> str:
        """
        First-pass PII removal using regex patterns.
        This runs BEFORE sending to LLM for additional safety.
        """
        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Phone numbers (various formats)
        text = re.sub(r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE]', text)
        
        # URLs and LinkedIn profiles
        text = re.sub(r'https?://[^\s]+', '[URL]', text)
        text = re.sub(r'linkedin\.com/in/[^\s]+', '[LINKEDIN]', text)
        
        # Physical addresses (basic pattern)
        text = re.sub(r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\.?(?:\s*,\s*[\w\s]+)?(?:\s*,\s*[A-Z]{2}\s*\d{5})?', '[ADDRESS]', text, flags=re.IGNORECASE)
        
        # ZIP codes
        text = re.sub(r'\b\d{5}(?:-\d{4})?\b', '[ZIP]', text)
        
        return text

    async def parse_resume(self, text: str, anonymize: bool = True) -> ParsedProfile:
        """
        Parse resume text and extract structured profile data.
        
        Args:
            text: Raw resume text (from PDF or plain text)
            anonymize: Whether to strip PII (default True for blind evaluation)
        
        Returns:
            ParsedProfile with extracted skills and competencies
        """
        # Pre-process: strip obvious PII
        if anonymize:
            text = self._strip_pii_regex(text)
        
        # If no AI client configured, return basic extraction
        if self.client is None:
            return self._fallback_parse(text)
        
        # Build the prompt
        user_prompt = f"""Parse the following resume and extract structured information.
Remember: DO NOT include any personal identifying information (names, emails, specific company/school names).

RESUME TEXT:
{text}

Return ONLY valid JSON matching the specified format."""

        try:
            # Call appropriate AI API
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.settings.default_model,
                    max_tokens=self.settings.max_tokens,
                    temperature=self.settings.temperature,
                    system=self.SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                content = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=self.settings.max_tokens,
                    temperature=self.settings.temperature,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.choices[0].message.content
            
            # Parse JSON response
            parsed_data = self._extract_json(content)
            
            # Convert to ParsedProfile
            return self._build_profile(parsed_data, text[:200] if not anonymize else None)
            
        except Exception as e:
            # Log error and return fallback
            print(f"Parser Agent error: {e}")
            return self._fallback_parse(text)
    
    def _extract_json(self, content: str) -> dict:
        """Extract JSON from LLM response, handling markdown code blocks"""
        # Try to find JSON in code blocks first
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if json_match:
            content = json_match.group(1)
        
        # Clean and parse
        content = content.strip()
        return json.loads(content)
    
    def _build_profile(self, data: dict, raw_preview: Optional[str] = None) -> ParsedProfile:
        """Convert parsed JSON data to ParsedProfile schema"""
        # Build skills list
        skills = []
        for skill_data in data.get("skills", []):
            skills.append(Skill(
                name=skill_data.get("name", ""),
                proficiency=ProficiencyLevel(skill_data.get("proficiency", "intermediate")),
                years_experience=skill_data.get("years_experience"),
                context=skill_data.get("context")
            ))
        
        # Map experience level
        exp_level_str = data.get("experience_level", "intermediate").lower()
        try:
            exp_level = ProficiencyLevel(exp_level_str)
        except ValueError:
            exp_level = ProficiencyLevel.INTERMEDIATE
        
        return ParsedProfile(
            competency_clusters=data.get("competency_clusters", {}),
            skills=skills,
            experience_years=data.get("experience_years"),
            experience_level=exp_level,
            education_level=data.get("education_level"),
            certifications=data.get("certifications", []),
            achievements=data.get("achievements", []),
            industries=data.get("industries", []),
            confidence_score=data.get("confidence_score", 0.8),
            raw_text_preview=raw_preview
        )
    
    def _fallback_parse(self, text: str) -> ParsedProfile:
        """
        Basic regex-based parsing when LLM is not available.
        Used for testing or when API keys are not configured.
        """
        # Common skill keywords to look for
        tech_skills = [
            "python", "javascript", "java", "c++", "sql", "react", "node.js",
            "aws", "azure", "docker", "kubernetes", "git", "html", "css",
            "typescript", "go", "rust", "scala", "r", "matlab", "tableau",
            "excel", "powerpoint", "word", "jira", "confluence", "slack"
        ]
        
        soft_skills = [
            "leadership", "communication", "teamwork", "problem-solving",
            "project management", "agile", "scrum", "mentoring", "presentation"
        ]
        
        text_lower = text.lower()
        
        # Find matching skills
        found_tech = [s for s in tech_skills if s in text_lower]
        found_soft = [s for s in soft_skills if s in text_lower]
        
        # Build clusters
        clusters = {}
        if found_tech:
            clusters["technical_skills"] = found_tech
        if found_soft:
            clusters["soft_skills"] = found_soft
        
        # Basic experience detection
        years_match = re.search(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', text_lower)
        exp_years = float(years_match.group(1)) if years_match else None
        
        # Education detection
        education = None
        if "phd" in text_lower or "doctorate" in text_lower:
            education = "PhD"
        elif "master" in text_lower or "mba" in text_lower:
            education = "Master's"
        elif "bachelor" in text_lower or "b.s." in text_lower or "b.a." in text_lower:
            education = "Bachelor's"
        elif "bootcamp" in text_lower or "certificate" in text_lower:
            education = "Certificate/Bootcamp"
        
        return ParsedProfile(
            competency_clusters=clusters,
            skills=[Skill(name=s, proficiency=ProficiencyLevel.INTERMEDIATE) for s in found_tech + found_soft],
            experience_years=exp_years,
            experience_level=ProficiencyLevel.INTERMEDIATE,
            education_level=education,
            certifications=[],
            achievements=[],
            industries=[],
            confidence_score=0.5,  # Low confidence for fallback
            raw_text_preview=None
        )
