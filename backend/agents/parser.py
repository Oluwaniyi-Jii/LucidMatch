<<<<<<< HEAD
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
            return {"error": "Failed to parse resume"}
=======
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
        Advanced regex-based parsing when LLM is not available.
        Extracts skills, experience, education, achievements, and more.
        """
        text_lower = text.lower()
        
        # === EXPANDED SKILL DETECTION ===
        tech_skills = [
            # Programming languages
            "python", "javascript", "java", "c++", "c#", "sql", "typescript", "go", "rust", 
            "scala", "r", "matlab", "php", "ruby", "swift", "kotlin",
            # Frameworks & Libraries
            "react", "angular", "vue", "node.js", "fastapi", "django", "flask", "spring",
            "express", "next.js", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
            # Databases
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "sqlite",
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
            "linux", "unix", "bash", "shell",
            # Tools
            "git", "github", "gitlab", "jira", "confluence", "slack", "figma", "sketch",
            # Data & Analytics
            "tableau", "power bi", "looker", "excel", "spss", "sas", "hadoop", "spark",
            "kafka", "airflow", "etl", "data warehouse", "machine learning", "deep learning",
            # Other technical
            "api", "rest", "graphql", "microservices", "html", "css", "sass"
        ]
        
        soft_skills = [
            "leadership", "communication", "teamwork", "collaboration", "problem-solving",
            "problem solving", "analytical", "critical thinking", "decision-making",
            "project management", "time management", "organization", "planning",
            "agile", "scrum", "kanban", "lean", "six sigma",
            "mentoring", "coaching", "training", "teaching", "facilitation",
            "presentation", "public speaking", "negotiation", "stakeholder management",
            "customer service", "client relations", "sales", "marketing",
            "research", "analysis", "documentation", "technical writing",
            "creative", "innovation", "strategic thinking", "budgeting"
        ]
        
        domain_skills = [
            # Healthcare
            "patient care", "clinical", "nursing", "medical", "healthcare", "hipaa",
            "emr", "epic", "cerner", "patient assessment", "diagnosis",
            # UX/Design
            "user research", "ux design", "ui design", "wireframing", "prototyping",
            "usability testing", "user interviews", "journey mapping", "design thinking",
            # Finance
            "financial analysis", "accounting", "budgeting", "forecasting", "audit",
            "risk management", "compliance", "investment", "trading",
            # HR
            "recruiting", "talent acquisition", "onboarding", "performance management",
            "employee relations", "compensation", "benefits",
            # Legal
            "contract", "legal research", "compliance", "regulatory"
        ]
        
        # Find all matching skills
        found_tech = []
        found_soft = []
        found_domain = []
        
        for skill in tech_skills:
            if skill in text_lower:
                found_tech.append(skill.title() if len(skill) > 3 else skill.upper())
        
        for skill in soft_skills:
            if skill in text_lower:
                found_soft.append(skill.title())
        
        for skill in domain_skills:
            if skill in text_lower:
                found_domain.append(skill.title())
        
        # Deduplicate
        found_tech = list(dict.fromkeys(found_tech))[:15]
        found_soft = list(dict.fromkeys(found_soft))[:10]
        found_domain = list(dict.fromkeys(found_domain))[:10]
        
        # Build clusters
        clusters = {}
        if found_tech:
            clusters["Technical Skills"] = found_tech
        if found_soft:
            clusters["Soft Skills"] = found_soft
        if found_domain:
            clusters["Domain Expertise"] = found_domain
        
        # === EXPERIENCE DETECTION ===
        years_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d{4})\s*[-–]\s*(?:present|current|now)',  # Calculate from date range
        ]
        
        exp_years = None
        for pattern in years_patterns[:-1]:
            match = re.search(pattern, text_lower)
            if match:
                exp_years = float(match.group(1))
                break
        
        # Try date range calculation
        if exp_years is None:
            date_match = re.search(r'(\d{4})\s*[-–]\s*(?:present|current|now|2026|2025|2024)', text_lower)
            if date_match:
                start_year = int(date_match.group(1))
                exp_years = 2026 - start_year
        
        # Experience level based on years
        if exp_years:
            if exp_years >= 10:
                exp_level = ProficiencyLevel.EXPERT
            elif exp_years >= 5:
                exp_level = ProficiencyLevel.ADVANCED
            elif exp_years >= 2:
                exp_level = ProficiencyLevel.INTERMEDIATE
            else:
                exp_level = ProficiencyLevel.BEGINNER
        else:
            exp_level = ProficiencyLevel.INTERMEDIATE
        
        # === EDUCATION DETECTION ===
        education = None
        if any(term in text_lower for term in ["ph.d", "phd", "doctorate", "doctor of"]):
            education = "PhD"
        elif any(term in text_lower for term in ["master", "mba", "m.s.", "m.a.", "msc", "master's"]):
            education = "Master's Degree"
        elif any(term in text_lower for term in ["bachelor", "b.s.", "b.a.", "bsc", "undergraduate"]):
            education = "Bachelor's Degree"
        elif any(term in text_lower for term in ["associate", "a.s.", "a.a."]):
            education = "Associate Degree"
        elif any(term in text_lower for term in ["bootcamp", "coding bootcamp", "intensive program"]):
            education = "Bootcamp Certificate"
        elif "certificate" in text_lower or "certification" in text_lower:
            education = "Professional Certificate"
        elif "high school" in text_lower or "diploma" in text_lower:
            education = "High School Diploma"
        
        # === CERTIFICATIONS ===
        cert_patterns = [
            r'certified\s+(\w+(?:\s+\w+)?)',
            r'(\w+)\s+certification',
            r'(aws|azure|gcp|pmp|scrum|cissp|cpa|cfa|six sigma)(?:\s+certified)?',
        ]
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) > 2:
                    certifications.append(match.upper() if len(match) <= 5 else match.title())
        certifications = list(dict.fromkeys(certifications))[:5]
        
        # === ACHIEVEMENTS ===
        achievements = []
        # Look for lines with numbers (quantified achievements)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Skip short lines or headers
            if len(line) < 20:
                continue
            # Look for achievement indicators
            if any(indicator in line.lower() for indicator in [
                'increased', 'decreased', 'reduced', 'improved', 'grew', 'achieved',
                'saved', 'generated', 'launched', 'led', 'managed', 'built',
                'developed', 'created', 'implemented', 'delivered', 'awarded',
                '%', '$', 'million', 'thousand', 'team of'
            ]):
                # Clean bullet points
                clean = re.sub(r'^[\s•\-\*·]+', '', line).strip()
                if len(clean) > 15:
                    achievements.append(clean[:150])
        achievements = achievements[:8]
        
        # === INDUSTRIES ===
        industries = []
        industry_keywords = {
            'healthcare': ['hospital', 'clinic', 'medical', 'patient', 'healthcare', 'nursing'],
            'technology': ['software', 'tech', 'startup', 'saas', 'it ', 'information technology'],
            'finance': ['bank', 'financial', 'investment', 'trading', 'fintech', 'insurance'],
            'consulting': ['consulting', 'advisory', 'deloitte', 'mckinsey', 'bcg', 'pwc', 'ey', 'kpmg'],
            'retail': ['retail', 'e-commerce', 'ecommerce', 'store', 'sales'],
            'education': ['university', 'school', 'college', 'teaching', 'academic'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
        }
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                industries.append(industry.title())
        
        # === CONFIDENCE SCORE ===
        # Based on how much info we extracted
        confidence_factors = 0
        if len(found_tech) + len(found_soft) >= 5: confidence_factors += 0.2
        if exp_years: confidence_factors += 0.2
        if education: confidence_factors += 0.2
        if len(achievements) >= 2: confidence_factors += 0.2
        if len(text) >= 500: confidence_factors += 0.1
        if len(text) >= 1000: confidence_factors += 0.1
        
        confidence_score = min(0.9, 0.3 + confidence_factors)
        
        # === BUILD PROFILE ===
        all_skills = found_tech + found_soft + found_domain
        skills = [
            Skill(
                name=s, 
                proficiency=ProficiencyLevel.ADVANCED if s in found_tech[:5] else ProficiencyLevel.INTERMEDIATE
            ) 
            for s in all_skills
        ]
        
        return ParsedProfile(
            competency_clusters=clusters,
            skills=skills,
            experience_years=exp_years,
            experience_level=exp_level,
            education_level=education,
            certifications=certifications,
            achievements=achievements,
            industries=industries,
            confidence_score=confidence_score,
            raw_text_preview=text[:200] if text else None
        )
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
