"""
Pydantic schemas for LucidMatch API
Defines data structures for profiles, jobs, matches, and API responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CompetencyLevel(str, Enum):
    STRONG = "strong"
    MID = "mid"
    LOW = "low"


class GapPriority(str, Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    NICE_TO_HAVE = "nice_to_have"


class ConfidenceLevel(str, Enum):
    HIGH = "high"      # ±2-5%
    MEDIUM = "medium"  # ±5-10%
    LOW = "low"        # ±10%+


# ============================================================================
# Skill & Competency Models
# ============================================================================

class Skill(BaseModel):
    """Individual skill with proficiency level"""
    name: str
    proficiency: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE
    years_experience: Optional[float] = None
    context: Optional[str] = None  # Where/how skill was used


class CompetencyCluster(BaseModel):
    """Group of related skills forming a competency area"""
    name: str
    skills: list[str]
    overall_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE


class SkillGap(BaseModel):
    """Identified gap between candidate and role requirements"""
    skill: str
    priority: GapPriority
    current_level: Optional[ProficiencyLevel] = None
    required_level: ProficiencyLevel
    learning_time_weeks: Optional[int] = None


# ============================================================================
# Profile Models (Output from Parser)
# ============================================================================

class ParsedProfile(BaseModel):
    """Anonymized candidate profile after parsing"""
    competency_clusters: dict[str, list[str]]  # e.g., {"data_analysis": ["Python", "SQL"]}
    skills: list[Skill]
    experience_years: Optional[float] = None
    experience_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE
    education_level: Optional[str] = None  # e.g., "Bachelor's", "Master's", "PhD", "Bootcamp"
    certifications: list[str] = []
    achievements: list[str] = []  # Notable impacts/accomplishments
    industries: list[str] = []  # Industries worked in
    confidence_score: float = Field(ge=0, le=1, default=0.8)
    raw_text_preview: Optional[str] = None  # First 200 chars for debugging (anonymized)


# ============================================================================
# Job Description Models
# ============================================================================

class JobRequirement(BaseModel):
    """Single requirement from a job description"""
    skill: str
    importance: GapPriority = GapPriority.IMPORTANT
    required_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE


class JobDescription(BaseModel):
    """Structured job description"""
    id: str
    title: str
    department: Optional[str] = None
    description: str
    required_skills: list[JobRequirement]
    preferred_skills: list[str] = []
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    education_required: Optional[str] = None
    industry: Optional[str] = None


# ============================================================================
# Match & Reasoning Models (Output from Reasoner)
# ============================================================================

class SkillTransfer(BaseModel):
    """Transfer efficiency between candidate skill and job requirement"""
    candidate_skill: str
    job_requirement: str
    transfer_efficiency: float = Field(ge=0, le=100)  # 0-100%
    reasoning: str


class MatchResult(BaseModel):
    """Complete match result from Reasoner agent"""
    job_id: str
    job_title: str
    overall_score: float = Field(ge=0, le=100)  # 0-100%
    confidence_range: float = Field(ge=0, le=20, default=5)  # ±X%
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    competency_level: CompetencyLevel = CompetencyLevel.MID
    
    # Detailed breakdown
    skills_match_score: float = Field(ge=0, le=10)  # 1-10
    experience_match_score: float = Field(ge=0, le=10)
    education_match_score: float = Field(ge=0, le=10)
    achievement_match_score: float = Field(ge=0, le=10)
    
    # Reasoning trace
    skill_transfers: list[SkillTransfer] = []
    skill_gaps: list[SkillGap] = []
    reasoning_summary: str  # Human-readable explanation
    strengths: list[str] = []
    concerns: list[str] = []


# ============================================================================
# Upskilling Models (Output from Strategist)
# ============================================================================

class LearningResource(BaseModel):
    """A recommended learning resource"""
    title: str
    provider: str  # e.g., "Coursera", "edX", "LinkedIn Learning"
    url: Optional[str] = None
    duration_hours: Optional[int] = None
    skill_addressed: str


class UpskillPath(BaseModel):
    """Complete upskilling curriculum"""
    quick_wins: list[LearningResource] = []  # 1-2 weeks
    core_learning: list[LearningResource] = []  # 1-2 months
    total_time_weeks: Optional[int] = None
    priority_order: list[str] = []  # Skills in order of importance


# ============================================================================
# Audit Models (Output from Auditor)
# ============================================================================

class BiasFlag(BaseModel):
    """A potential bias detected in the matching"""
    category: str  # e.g., "socioeconomic_proxy", "gender_coded", "credential_bias"
    indicator: str  # What triggered the flag
    severity: str  # "low", "medium", "high"
    recommendation: str


class AuditResult(BaseModel):
    """Complete audit of a match decision"""
    match_id: str
    bias_flags: list[BiasFlag] = []
    fairness_score: float = Field(ge=0, le=100)  # 0-100%
    passed_audit: bool = True
    decision_log: str  # Plain English explanation
    counterfactual_note: Optional[str] = None  # Note about demographic parity


# ============================================================================
# API Request/Response Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze a resume"""
    resume_text: str
    anonymize: bool = True  # Strip PII before processing


class AnalyzeResponse(BaseModel):
    """Response from resume analysis"""
    profile: ParsedProfile
    processing_time_ms: int


class MatchRequest(BaseModel):
    """Request to match a profile against jobs"""
    profile: ParsedProfile
    job_ids: Optional[list[str]] = None  # If None, match against all jobs


class MatchResponse(BaseModel):
    """Response with all match results"""
    matches: list[MatchResult]
    top_match: Optional[MatchResult] = None
    processing_time_ms: int


class FullAnalysisRequest(BaseModel):
    """Request for complete analysis pipeline"""
    resume_text: str
    job_ids: Optional[list[str]] = None
    include_upskilling: bool = True
    include_audit: bool = True


class FullAnalysisResponse(BaseModel):
    """Complete analysis including parsing, matching, upskilling, and audit"""
    profile: ParsedProfile
    matches: list[MatchResult]
    top_match: Optional[MatchResult] = None
    upskill_path: Optional[UpskillPath] = None
    audit: Optional[AuditResult] = None
    total_processing_time_ms: int
