<<<<<<< HEAD
from anthropic import AsyncAnthropic
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, REASONER_MAX_TOKENS

class ReasonerAgent:
    """
    Comprehensive AI hiring evaluation agent specializing in resume-to-job matching.
    Uses 10 detailed criteria with 1-10 scoring for thorough candidate assessment.
    """
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def match_role(self, candidate_profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        prompt = f"""
You are an AI hiring evaluation agent specializing in resume-to-job matching.

Your task is to analyze a candidate's resume against the given job description to determine the candidate's overall fit for the role without any bias.

CANDIDATE PROFILE:
{json.dumps(candidate_profile, indent=2)}

JOB DESCRIPTION:
{job_description}

EVALUATION CRITERIA (Score each 1-10):

1. Education Level & Certifications
   - Assess alignment between education/certifications and job requirements
   - Score higher when qualifications meet or exceed requirements
   - Do not penalize if education is listed as preferred
   - Do not consider institution reputation

2. Quality of Experience
   - Evaluate relevance, depth, and impact of prior roles
   - Prioritize quantified achievements, scope of responsibility, role progression
   - Do not rely solely on organization type, job titles, or years

3. Skills Match (Technical & Soft Skills)
   - Compare resume skills to required and preferred skills
   - Score higher for exact or closely related skill matches
   - Separate proven skills from implied or unclear skills

4. Transferable Skills
   - Evaluate similarity of past roles, industries, responsibilities to target role
   - Consider how prior experience can reasonably transfer
   - Score lower when transferability is unclear or indirect
   - Score high on reasonably transferred skills

5. Core Competency
   - Assess evidence of foundational competencies critical to job performance
   - Use experience descriptions, accomplishments, responsibilities as evidence
   - Do not assume competency without demonstrated usage
   - Score high on proven or demonstrated competency
   - Score low if competency is unclear rather than assume

6. Potential Interpersonal Skills
   - Evaluate only interpersonal skills demonstrated through experience
   - Look for leadership, collaboration, stakeholder communication
   - Do not score based on self-claims without supporting examples

7. Gaps / Missing Skills
   - Identify required skills or qualifications absent from resume
   - Penalize missing required skills more than missing preferred skills
   - Do not penalize career gaps unless they directly affect requirements
   - Lower score = more critical gaps

8. Ability to Learn
   - Assess based on skill progression, role advancement, certifications earned, career transitions
   - Do not infer learning ability without observable indicators
   - Look for evidence of continuous learning and adaptation

9. Trainable Skills (Hard & Soft Skills)
   - Identify skills not currently demonstrated but reasonably learnable
   - Distinguish between trainable skills and missing critical skills
   - Score high and list trainable skills
   - Recommend pilot program and estimate learning time

10. Potential / Readiness
    - Evaluate whether candidate appears job-ready or requires significant ramp-up
    - Base readiness on experience relevance, skill coverage, learning indicators
    - Do not base readiness only on explicitly listed skills
    - Do not equate potential with readiness; score them separately
    - Provide visual insight comparing potential and readiness

SCORING RULES:
- Each criterion: 1-10 based solely on evidence
- Score Classification:
  * Low: 1-4
  * Medium: 5-7
  * High: 8-10

OVERALL EVALUATION:
- Total Score = Sum of all 10 criteria (max 100)
- Classification:
  * Low: 1-49
  * Medium: 50-79
  * High: 80-100

GENERAL RULES:
- Evaluate solely using resume and job description
- Evaluate potential skills based on detailed experience
- Evaluate explicitly listed skills as well
- Do not consider personal identifiers (race, gender, organizations, demographics)
- Assign score 1-10 for each criterion based only on available evidence
- If evidence is limited or unclear, assign lower score rather than guessing

KEYWORD STUFFING DETECTION (CRITICAL):
When evaluating Skills Match, Core Competency, and Quality of Experience, apply these rules:

1. SKILLS MUST HAVE EVIDENCE: A skill listed in a "Skills" section is worth NOTHING without supporting evidence in Experience or Projects
   - Example: Listing "Kubernetes" but only showing IT Support experience = 0 credit for Kubernetes
   - Example: Listing "Machine Learning" but only building a calculator = 0 credit for ML

2. MISMATCH PENALTY: If the number of claimed technologies (10+) vastly exceeds demonstrated projects (1-3 simple ones), apply severe penalty
   - This is a RED FLAG indicating resume padding
   - Score Skills Match as LOW (1-3) regardless of keyword presence

3. EXPERIENCE-SKILL GAP: Compare claimed seniority to actual experience
   - Claiming "Senior" skills with only IT Support/Help Desk background = LOW score
   - Freelance "various projects" without specifics = unverifiable = LOW score

4. PROJECT QUALITY CHECK:
   - "Todo App", "Calculator", "Portfolio Website" are BEGINNER projects
   - These do NOT demonstrate advanced skills like microservices, ML, or distributed systems
   - Penalize heavily if advanced skills are claimed but only beginner projects shown

5. CERTIFICATION QUALITY:
   - "Started", "In Progress", "2-hour course" = NOT meaningful credentials
   - Only completed, recognized certifications count as evidence

6. QUANTIFICATION CHECK:
   - Vague claims like "worked on projects" or "helped customers" = LOW evidence
   - Specific metrics like "reduced latency by 40%" or "managed team of 12" = HIGH evidence
   - Absence of ANY quantified achievements in a senior-level application = RED FLAG

OUTPUT FORMAT (JSON ONLY):
{{
  "overall_evaluation": {{
    "total_score": 0,
    "fit_level": "Low | Medium | High",
    "summary": "Brief 2-3 sentence summary of overall fit"
  }},
  "criteria_scores": {{
    "education_certifications": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Specific evidence from resume",
      "justification": "Why this score was assigned"
    }},
    "quality_of_experience": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Quantified achievements and impact",
      "justification": "Analysis of experience quality"
    }},
    "skills_match": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Matched skills listed",
      "technical_skills_matched": ["skill1", "skill2"],
      "soft_skills_matched": ["skill1", "skill2"],
      "justification": "Skill alignment analysis"
    }},
    "transferable_skills": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Examples of transferable experience",
      "transferable_items": [
        {{"from": "previous skill/role", "to": "target requirement", "efficiency": "High|Medium|Low"}}
      ],
      "justification": "Transfer efficiency analysis"
    }},
    "core_competency": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Demonstrated competencies",
      "competencies_proven": ["competency1", "competency2"],
      "justification": "Core competency assessment"
    }},
    "interpersonal_skills": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Demonstrated interpersonal abilities",
      "skills_identified": ["leadership", "collaboration", "communication"],
      "justification": "Interpersonal skills analysis"
    }},
    "gaps_missing_skills": {{
      "score": 0,
      "level": "Low | Medium | High",
      "required_gaps": ["critical missing skill 1"],
      "preferred_gaps": ["nice-to-have missing skill 1"],
      "impact_assessment": "How critical are these gaps",
      "justification": "Gap analysis"
    }},
    "ability_to_learn": {{
      "score": 0,
      "level": "Low | Medium | High",
      "evidence": "Learning indicators observed",
      "learning_indicators": ["skill progression", "certifications", "role transitions"],
      "justification": "Learning ability assessment"
    }},
    "trainable_skills": {{
      "score": 0,
      "level": "Low | Medium | High",
      "skills_identified": ["trainable skill 1", "trainable skill 2"],
      "recommended_pilot_program": "Suggested training approach",
      "estimated_learning_time": "X weeks/months",
      "justification": "Trainability assessment"
    }},
    "potential_readiness": {{
      "score": 0,
      "potential_score": 0,
      "readiness_score": 0,
      "potential_level": "Low | Medium | High",
      "readiness_level": "Low | Medium | High",
      "evidence": "Indicators of potential and readiness",
      "justification": "Separate analysis of potential vs current readiness",
      "ramp_up_time_estimate": "X weeks/months"
    }}
  }},
  "final_summary": "Comprehensive 3-4 sentence summary with hiring recommendation",
  "hiring_recommendation": "Strong Hire | Hire | Maybe | Pass",
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "key_concerns": ["concern 1", "concern 2"],
  "radar_chart_data": [
    {{"subject": "Education", "score": 0, "fullMark": 10}},
    {{"subject": "Experience", "score": 0, "fullMark": 10}},
    {{"subject": "Skills Match", "score": 0, "fullMark": 10}},
    {{"subject": "Transferability", "score": 0, "fullMark": 10}},
    {{"subject": "Core Competency", "score": 0, "fullMark": 10}},
    {{"subject": "Interpersonal", "score": 0, "fullMark": 10}},
    {{"subject": "Learning Ability", "score": 0, "fullMark": 10}},
    {{"subject": "Trainability", "score": 0, "fullMark": 10}},
  "radar_chart_data": [
    {{"subject": "Education", "score": 0, "fullMark": 10}},
    {{"subject": "Experience", "score": 0, "fullMark": 10}},
    {{"subject": "Skills Match", "score": 0, "fullMark": 10}},
    {{"subject": "Transferability", "score": 0, "fullMark": 10}},
    {{"subject": "Core Competency", "score": 0, "fullMark": 10}},
    {{"subject": "Interpersonal", "score": 0, "fullMark": 10}},
    {{"subject": "Learning Ability", "score": 0, "fullMark": 10}},
    {{"subject": "Trainability", "score": 0, "fullMark": 10}},
    {{"subject": "Potential", "score": 0, "fullMark": 10}},
    {{"subject": "Readiness", "score": 0, "fullMark": 10}}
  ],
  "evidence": [
    {{"requirement": "Key Requirement from Job", "quote": "Exact quote from resume supporting match", "score": 0-100}}
  ]
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just the JSON object.
"""

        try:
            message = await self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=4096,  # Increased for detailed response
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            result = json.loads(json_str)
            
            # Ensure output has evidence array even if model misses it
            if "evidence" not in result:
                result["evidence"] = []
            
            # Ensure backward compatibility with old format
            result['match_score'] = result['overall_evaluation']['total_score']
            result['confidence_score'] = 0.95 if result['overall_evaluation']['total_score'] >= 70 else 0.75
            result['reasoning'] = result['overall_evaluation']['summary']
            
            return result
            
        except Exception as e:
            print(f"Reasoner Error: {e}")
            return {
                "error": "Failed to evaluate candidate",
                "match_score": 0,
                "overall_evaluation": {
                    "total_score": 0,
                    "fit_level": "Low",
                    "summary": "Evaluation failed"
                }
            }
=======
"""
Reasoner Agent - Role Matching & Transfer Efficiency

The Reasoner Agent is the core intelligence engine that:
1. Compares candidate skills against job requirements
2. Calculates "Transfer Efficiency" - how well Skill A prepares someone for Job Requirement B
3. Provides match scores with confidence ranges
4. Generates detailed reasoning traces explaining the "why" behind matches
"""

import json
import re
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI

from config import get_settings, Settings
from schemas import (
    ParsedProfile,
    JobDescription,
    MatchResult,
    SkillTransfer,
    SkillGap,
    CompetencyLevel,
    ConfidenceLevel,
    GapPriority,
    ProficiencyLevel
)


class ReasonerAgent:
    """
    Evaluates candidate-job fit using transfer efficiency logic.
    Goes beyond keyword matching to understand skill transferability.
    """
    
    SYSTEM_PROMPT = """You are an expert talent matching AI that evaluates candidate fit for roles.
Your specialty is recognizing TRANSFERABLE SKILLS - understanding how experience in one domain prepares someone for success in another.

KEY PRINCIPLES:
1. Skills transfer across domains (e.g., nurse's crisis management → UX researcher's user advocacy)
2. Demonstrated ability > credentials (portfolio > degree for many roles)
3. Learning velocity matters (self-taught skills show adaptability)
4. Context matters (leading a team of 50 ≠ managing 3 people)

TRANSFER EFFICIENCY SCORING (0-100%):
- 90-100%: Direct match (Python → Python requirement)
- 70-89%: High transfer (Data Analysis in Finance → Product Analytics)
- 50-69%: Moderate transfer (Project Management → Technical PM, needs some upskilling)
- 30-49%: Partial transfer (Teaching → Corporate Training, significant gaps)
- 0-29%: Low transfer (unrelated skills)

MATCH SCORING CRITERIA (each 1-10):
1. Skills Match: Technical and soft skills alignment
2. Experience Match: Years and role similarity
3. Education Match: Required credentials and relevant learning
4. Achievement Match: Demonstrated impact and results

CONFIDENCE RANGES:
- ±2-5%: Rich candidate data, clear skill evidence (HIGH confidence)
- ±5-10%: Some gaps in information (MEDIUM confidence)
- ±10%+: Sparse resume, unusual background (LOW confidence)

COMPETENCY CLASSIFICATION:
- Strong: Overall score 75%+, minimal critical gaps
- Mid: Overall score 50-74%, addressable gaps
- Low: Overall score <50%, significant gaps

OUTPUT FORMAT (JSON):
{
    "overall_score": 78,
    "confidence_range": 5,
    "confidence_level": "high",
    "competency_level": "strong",
    "skills_match_score": 8,
    "experience_match_score": 7,
    "education_match_score": 6,
    "achievement_match_score": 8,
    "skill_transfers": [
        {
            "candidate_skill": "Patient Advocacy",
            "job_requirement": "User Research",
            "transfer_efficiency": 75,
            "reasoning": "Experience advocating for patient needs translates directly to understanding and advocating for user needs in UX research."
        }
    ],
    "skill_gaps": [
        {
            "skill": "Figma",
            "priority": "important",
            "current_level": null,
            "required_level": "intermediate",
            "learning_time_weeks": 3
        }
    ],
    "reasoning_summary": "Candidate shows strong potential for this role despite non-traditional background...",
    "strengths": ["Crisis decision-making", "Stakeholder communication"],
    "concerns": ["No formal UX training", "May need tool-specific onboarding"]
}

IMPORTANT: Always explain your reasoning. The explanation IS the product, not just the score."""

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

    async def evaluate_match(
        self, 
        candidate_profile: ParsedProfile, 
        job_description: JobDescription
    ) -> MatchResult:
        """
        Evaluate how well a candidate matches a job description.
        
        Args:
            candidate_profile: Parsed and anonymized candidate profile
            job_description: Structured job description with requirements
        
        Returns:
            MatchResult with scores, reasoning, and identified gaps
        """
        if self.client is None:
            return self._fallback_match(candidate_profile, job_description)
        
        # Build the evaluation prompt
        user_prompt = self._build_evaluation_prompt(candidate_profile, job_description)
        
        try:
            # Call AI API
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
            
            # Parse and build result
            parsed_data = self._extract_json(content)
            return self._build_match_result(parsed_data, job_description)
            
        except Exception as e:
            print(f"Reasoner Agent error: {e}")
            return self._fallback_match(candidate_profile, job_description)
    
    def _build_evaluation_prompt(
        self, 
        profile: ParsedProfile, 
        job: JobDescription
    ) -> str:
        """Build the prompt for job-candidate evaluation"""
        # Format candidate skills
        skills_text = []
        for cluster_name, skills in profile.competency_clusters.items():
            skills_text.append(f"  {cluster_name}: {', '.join(skills)}")
        
        detailed_skills = []
        for skill in profile.skills:
            detail = f"  - {skill.name} ({skill.proficiency.value})"
            if skill.years_experience:
                detail += f", {skill.years_experience} years"
            if skill.context:
                detail += f" - {skill.context}"
            detailed_skills.append(detail)
        
        # Format job requirements
        required = []
        for req in job.required_skills:
            required.append(f"  - {req.skill} ({req.required_level.value}, {req.importance.value})")
        
        return f"""Evaluate this candidate for the following role.

=== CANDIDATE PROFILE ===
Experience Level: {profile.experience_level.value}
Years of Experience: {profile.experience_years or 'Not specified'}
Education: {profile.education_level or 'Not specified'}
Certifications: {', '.join(profile.certifications) if profile.certifications else 'None listed'}

Competency Clusters:
{chr(10).join(skills_text) if skills_text else '  None identified'}

Detailed Skills:
{chr(10).join(detailed_skills) if detailed_skills else '  None identified'}

Key Achievements:
{chr(10).join(['  - ' + a for a in profile.achievements]) if profile.achievements else '  None listed'}

Industries: {', '.join(profile.industries) if profile.industries else 'Not specified'}

=== JOB DESCRIPTION ===
Title: {job.title}
Department: {job.department or 'Not specified'}
Industry: {job.industry or 'Not specified'}

Description:
{job.description}

Required Skills:
{chr(10).join(required) if required else '  None specified'}

Preferred Skills: {', '.join(job.preferred_skills) if job.preferred_skills else 'None listed'}

Experience Required: {job.experience_years_min or 0}-{job.experience_years_max or 'any'} years
Education Required: {job.education_required or 'Not specified'}

=== INSTRUCTIONS ===
Analyze the candidate's fit for this role. Focus on:
1. Direct skill matches
2. Transferable skills from their background
3. Critical gaps that would need to be filled
4. Overall potential considering learning velocity

Return ONLY valid JSON matching the specified format."""

    def _extract_json(self, content: str) -> dict:
        """Extract JSON from LLM response"""
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        if json_match:
            content = json_match.group(1)
        content = content.strip()
        return json.loads(content)
    
    def _build_match_result(self, data: dict, job: JobDescription) -> MatchResult:
        """Convert parsed JSON to MatchResult schema"""
        # Build skill transfers
        transfers = []
        for t in data.get("skill_transfers", []):
            transfers.append(SkillTransfer(
                candidate_skill=t.get("candidate_skill", ""),
                job_requirement=t.get("job_requirement", ""),
                transfer_efficiency=t.get("transfer_efficiency", 0),
                reasoning=t.get("reasoning", "")
            ))
        
        # Build skill gaps
        gaps = []
        for g in data.get("skill_gaps", []):
            try:
                priority = GapPriority(g.get("priority", "important"))
            except ValueError:
                priority = GapPriority.IMPORTANT
            
            try:
                req_level = ProficiencyLevel(g.get("required_level", "intermediate"))
            except ValueError:
                req_level = ProficiencyLevel.INTERMEDIATE
            
            current = None
            if g.get("current_level"):
                try:
                    current = ProficiencyLevel(g.get("current_level"))
                except ValueError:
                    pass
            
            gaps.append(SkillGap(
                skill=g.get("skill", ""),
                priority=priority,
                current_level=current,
                required_level=req_level,
                learning_time_weeks=g.get("learning_time_weeks")
            ))
        
        # Map confidence level
        try:
            conf_level = ConfidenceLevel(data.get("confidence_level", "medium").lower())
        except ValueError:
            conf_level = ConfidenceLevel.MEDIUM
        
        # Map competency level
        try:
            comp_level = CompetencyLevel(data.get("competency_level", "mid").lower())
        except ValueError:
            comp_level = CompetencyLevel.MID
        
        return MatchResult(
            job_id=job.id,
            job_title=job.title,
            overall_score=data.get("overall_score", 50),
            confidence_range=data.get("confidence_range", 10),
            confidence_level=conf_level,
            competency_level=comp_level,
            skills_match_score=data.get("skills_match_score", 5),
            experience_match_score=data.get("experience_match_score", 5),
            education_match_score=data.get("education_match_score", 5),
            achievement_match_score=data.get("achievement_match_score", 5),
            skill_transfers=transfers,
            skill_gaps=gaps,
            reasoning_summary=data.get("reasoning_summary", ""),
            strengths=data.get("strengths", []),
            concerns=data.get("concerns", [])
        )
    
    def _fallback_match(
        self, 
        profile: ParsedProfile, 
        job: JobDescription
    ) -> MatchResult:
        """
        Advanced matching when LLM is not available.
        Uses multi-criteria scoring based on skills, experience, education, and achievements.
        """
        # === 1. SKILLS MATCHING (40% weight) ===
        candidate_skills = set()
        candidate_skills_list = []
        for skills in profile.competency_clusters.values():
            for s in skills:
                candidate_skills.add(s.lower())
                candidate_skills_list.append(s.lower())
        for skill in profile.skills:
            candidate_skills.add(skill.name.lower())
            candidate_skills_list.append(skill.name.lower())
        
        # Also extract keywords from raw text if available
        resume_text = getattr(profile, '_raw_text', '') or ''
        resume_lower = resume_text.lower()
        
        job_skills = set()
        job_required = []
        for req in job.required_skills:
            job_skills.add(req.skill.lower())
            job_required.append(req.skill.lower())
        for skill in job.preferred_skills:
            job_skills.add(skill.lower())
        
        # Direct skill matches
        direct_matches = candidate_skills.intersection(job_skills)
        
        # Fuzzy/partial matches (skill appears in resume text)
        fuzzy_matches = set()
        for job_skill in job_skills:
            if job_skill in resume_lower:
                fuzzy_matches.add(job_skill)
            # Check for partial matches
            for cand_skill in candidate_skills:
                if job_skill in cand_skill or cand_skill in job_skill:
                    fuzzy_matches.add(job_skill)
        
        all_matches = direct_matches.union(fuzzy_matches)
        
        if job_skills:
            skills_ratio = len(all_matches) / len(job_skills)
        else:
            skills_ratio = 0.3
        
        skills_score = min(10, int(skills_ratio * 10) + 1)  # 1-10 scale
        
        # === 2. EXPERIENCE MATCHING (25% weight) ===
        candidate_years = profile.experience_years or 0
        required_min = job.experience_years_min or 0
        required_max = job.experience_years_max or 10
        
        if candidate_years >= required_min:
            if candidate_years <= required_max + 2:
                experience_score = 8 + min(2, (candidate_years - required_min) / 2)
            else:
                # Overqualified - slight penalty
                experience_score = 7
        elif candidate_years >= required_min - 1:
            experience_score = 6
        elif candidate_years >= required_min - 2:
            experience_score = 4
        else:
            experience_score = max(2, candidate_years)
        
        experience_score = min(10, max(1, int(experience_score)))
        
        # === 3. EDUCATION MATCHING (20% weight) ===
        edu_levels = {
            'phd': 10, 'doctorate': 10, 'doctor': 10,
            'master': 8, 'masters': 8, 'mba': 8, 'ms': 8, 'ma': 8,
            'bachelor': 6, 'bachelors': 6, 'bs': 6, 'ba': 6, 'bsc': 6,
            'associate': 4, 'associates': 4,
            'diploma': 3, 'certificate': 3, 'bootcamp': 3,
            'high school': 2, 'ged': 2
        }
        
        candidate_edu = (profile.education_level or '').lower()
        candidate_edu_score = 3  # default
        for level, score in edu_levels.items():
            if level in candidate_edu:
                candidate_edu_score = score
                break
        
        required_edu = (job.education_required or '').lower()
        required_edu_score = 5  # default bachelor-ish
        for level, score in edu_levels.items():
            if level in required_edu:
                required_edu_score = score
                break
        
        if candidate_edu_score >= required_edu_score:
            education_score = 8 + min(2, (candidate_edu_score - required_edu_score) / 2)
        elif candidate_edu_score >= required_edu_score - 2:
            education_score = 6
        else:
            education_score = 4
        
        education_score = min(10, max(1, int(education_score)))
        
        # === 4. ACHIEVEMENTS MATCHING (15% weight) ===
        achievements = profile.achievements or []
        num_achievements = len(achievements)
        
        # Look for quantified achievements (numbers = good)
        quantified = sum(1 for a in achievements if any(c.isdigit() for c in a))
        
        if num_achievements >= 5 and quantified >= 2:
            achievement_score = 9
        elif num_achievements >= 3 and quantified >= 1:
            achievement_score = 7
        elif num_achievements >= 2:
            achievement_score = 5
        elif num_achievements >= 1:
            achievement_score = 4
        else:
            achievement_score = 2
        
        achievement_score = min(10, max(1, achievement_score))
        
        # === CALCULATE OVERALL SCORE ===
        # Weighted average: Skills 40%, Experience 25%, Education 20%, Achievements 15%
        overall_score = int(
            skills_score * 4.0 +
            experience_score * 2.5 +
            education_score * 2.0 +
            achievement_score * 1.5
        )
        overall_score = min(100, max(10, overall_score))
        
        # === CONFIDENCE LEVEL ===
        # Based on how much data we have
        data_completeness = 0
        if len(candidate_skills) >= 5: data_completeness += 1
        if profile.experience_years: data_completeness += 1
        if profile.education_level: data_completeness += 1
        if len(achievements) >= 2: data_completeness += 1
        
        if data_completeness >= 4:
            conf_level = ConfidenceLevel.HIGH
            conf_range = 5
        elif data_completeness >= 2:
            conf_level = ConfidenceLevel.MEDIUM
            conf_range = 10
        else:
            conf_level = ConfidenceLevel.LOW
            conf_range = 15
        
        # === COMPETENCY LEVEL ===
        if overall_score >= 70:
            comp_level = CompetencyLevel.STRONG
        elif overall_score >= 45:
            comp_level = CompetencyLevel.MID
        else:
            comp_level = CompetencyLevel.LOW
        
        # === SKILL GAPS ===
        gaps = []
        missing = job_skills - all_matches
        for skill in list(missing)[:5]:
            priority = GapPriority.CRITICAL if skill in job_required[:3] else GapPriority.IMPORTANT
            gaps.append(SkillGap(
                skill=skill.title(),
                priority=priority,
                required_level=ProficiencyLevel.INTERMEDIATE,
                learning_time_weeks=3 if priority == GapPriority.CRITICAL else 4
            ))
        
        # === SKILL TRANSFERS ===
        transfers = []
        transfer_mappings = {
            'patient': [('patient advocacy', 'user advocacy', 75), ('patient care', 'customer care', 70)],
            'nurse': [('clinical assessment', 'user research', 65), ('care planning', 'project planning', 60)],
            'teach': [('teaching', 'training', 80), ('curriculum', 'documentation', 65)],
            'retail': [('customer service', 'client relations', 70), ('sales', 'business development', 60)],
            'analysis': [('data analysis', 'analytics', 90), ('research', 'market research', 75)],
            'manage': [('team management', 'leadership', 85), ('project management', 'agile', 70)],
            'python': [('python', 'programming', 95), ('scripting', 'automation', 80)],
            'communication': [('communication', 'stakeholder management', 80)],
        }
        
        for keyword, mappings in transfer_mappings.items():
            if keyword in resume_lower:
                for cand_skill, job_skill, efficiency in mappings:
                    if any(job_skill in js.lower() or js.lower() in job_skill for js in job_skills):
                        transfers.append(SkillTransfer(
                            candidate_skill=cand_skill.title(),
                            job_requirement=job_skill.title(),
                            transfer_efficiency=efficiency,
                            reasoning=f"Experience with {cand_skill} transfers to {job_skill}"
                        ))
                        break
        
        # Limit transfers
        transfers = transfers[:5]
        
        # === BUILD REASONING ===
        strengths = []
        concerns = []
        
        if skills_score >= 7:
            strengths.append(f"Strong skill alignment ({len(all_matches)}/{len(job_skills)} skills)")
        elif skills_score >= 5:
            strengths.append(f"Moderate skill match ({len(all_matches)}/{len(job_skills)} skills)")
        else:
            concerns.append(f"Limited skill overlap ({len(all_matches)}/{len(job_skills)} skills)")
        
        if experience_score >= 7:
            strengths.append(f"{candidate_years} years experience meets requirements")
        elif experience_score < 5:
            concerns.append(f"Experience gap: {candidate_years} years vs {required_min}+ required")
        
        if education_score >= 7:
            strengths.append(f"Education ({profile.education_level}) meets or exceeds requirements")
        elif education_score < 5:
            concerns.append(f"Education level may not meet requirements")
        
        if achievement_score >= 7:
            strengths.append(f"{num_achievements} demonstrated achievements with measurable impact")
        elif achievement_score < 5:
            concerns.append("Limited quantifiable achievements")
        
        if len(transfers) > 0:
            strengths.append(f"Identified {len(transfers)} transferable skill areas")
        
        reasoning = f"Multi-criteria analysis: Skills {skills_score}/10, Experience {experience_score}/10, Education {education_score}/10, Achievements {achievement_score}/10. "
        if overall_score >= 70:
            reasoning += "Strong candidate with good overall fit."
        elif overall_score >= 50:
            reasoning += "Moderate fit with some areas for development."
        else:
            reasoning += "Significant gaps identified - may need substantial upskilling."
        
        return MatchResult(
            job_id=job.id,
            job_title=job.title,
            overall_score=overall_score,
            confidence_range=conf_range,
            confidence_level=conf_level,
            competency_level=comp_level,
            skills_match_score=skills_score,
            experience_match_score=experience_score,
            education_match_score=education_score,
            achievement_match_score=achievement_score,
            skill_transfers=transfers,
            skill_gaps=gaps,
            reasoning_summary=reasoning,
            strengths=strengths[:4],
            concerns=concerns[:4]
        )
    
    async def evaluate_multiple_jobs(
        self, 
        profile: ParsedProfile, 
        jobs: list[JobDescription]
    ) -> list[MatchResult]:
        """
        Evaluate a candidate against multiple job descriptions.
        Returns results sorted by match score (highest first).
        """
        results = []
        for job in jobs:
            result = await self.evaluate_match(profile, job)
            results.append(result)
        
        # Sort by overall score descending
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
