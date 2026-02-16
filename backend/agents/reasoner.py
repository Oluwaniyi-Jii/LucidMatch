from anthropic import AsyncAnthropic
import json
import logging
from typing import Dict, Any

from config import ANTHROPIC_API_KEY, OPUS_MODEL, REASONER_MAX_TOKENS
from exceptions import ReasonerError
from utils.agent_utils import AgentResponseParser
from constants import AgentDefaults

logger = logging.getLogger(__name__)


class ReasonerAgent:
    """
    Comprehensive AI hiring evaluation agent specializing in resume-to-job matching.
    Uses 10 detailed criteria with 1-10 scoring for thorough candidate assessment.
    """
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.parser = AgentResponseParser()


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

QUALITY CONTROL & ANTI-GAMING (CRITICAL):
1. SPARSE RESUME / LOW EFFORT DETECTION:
   - If the resume contains minimal information (e.g., only job titles, < 50 words total, or genetic statements like "Did marketing", "Used computers"), you MUST assign scores of 1-2 for:
     * Quality of Experience
     * Skills Match
     * Core Competency
     * Potential / Readiness
   - "Did marketing" does NOT imply detailed knowledge of strategy, SEO, or analytics. Do not give benefit of the doubt.
   - If description is extremely vague, assume NO competence.

2. NO HALLUCINATION:
   - Do NOT infer skills or experience not explicitly written.
   - Do NOT fill in gaps with "implied" knowledge.
   - Evidence fields MUST contain actual text from the resume or "None provided".

3. KEYWORD STUFFING:
   - Skills listed without supporting evidence in Experience = 0 credit.
   - Mismatch between claimed seniority and actual descriptions (e.g., "Senior" role with "fixed printer" description) = Low Score.
   - Penalize "keyword dumps" where candidate lists 20+ technologies but shows 0 projects using them.

4. PROJECT/EXPERIENCE QUALITY:
   - "Todo App", "Calculator", or generic course projects = Beginner level (Low Score).
   - Vague claims ("worked on stuff") = Low Score.
   - Lack of metrics/quantification in what should be a professional role = Low Score.

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
            logger.info("Calling Reasoner Agent")
            message = await self.client.messages.create(
                model=OPUS_MODEL,
                max_tokens=4096,  # Increased for detailed response
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            result = self.parser.extract_json(content)
            
            # Ensure output has evidence array even if model misses it
            result = self.parser.ensure_field(result, "evidence", [])
            
            # Ensure backward compatibility with old format
            if "overall_evaluation" in result:
                result['match_score'] = result['overall_evaluation']['total_score']
                result['confidence_score'] = AgentDefaults.DEFAULT_CONFIDENCE if result['overall_evaluation']['total_score'] >= 70 else 0.75
                result['reasoning'] = result['overall_evaluation']['summary']
            else:
                logger.warning("Missing overall_evaluation in response")
                result['match_score'] = AgentDefaults.FALLBACK_MATCH_SCORE
                result['confidence_score'] = AgentDefaults.DEFAULT_CONFIDENCE
            
            logger.info(f"Reasoner Agent completed: match_score={result['match_score']}")
            return result
            
        except Exception as e:
            logger.error(f"Reasoner Agent failed: {e}", exc_info=True)
            raise ReasonerError(f"Failed to evaluate candidate: {str(e)}")
