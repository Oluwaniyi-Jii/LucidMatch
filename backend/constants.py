"""
Centralized constants for LucidMatch backend.
Contains magic values, thresholds, and configuration constants.
"""

# File Upload Configuration
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = {'.pdf', '.txt', '.docx'}

# Candidate Defaults
ANONYMOUS_CANDIDATE_NAME = "Anonymous Candidate"

# Score Thresholds
class ScoreThresholds:
    """Score classification thresholds"""
    HIGH = 80
    MEDIUM = 50
    LOW = 0

# Analysis Status
class AnalysisStatus:
    """Status values for candidate analyses"""
    NEW = "new"
    REVIEWED = "reviewed"
    FLAGGED = "flagged"
    CLEAN = "clean"

# Competency Levels
class CompetencyLevel:
    """Competency level classifications"""
    STRONG = "strong"
    MID = "mid"
    LOW = "low"

# Confidence Levels
class ConfidenceLevel:
    """Confidence level classifications"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Agent Configuration
class AgentDefaults:
    """Default values for agent responses"""
    FALLBACK_FAIRNESS_SCORE = 100
    FALLBACK_MATCH_SCORE = 0
    DEFAULT_CONFIDENCE = 0.8
