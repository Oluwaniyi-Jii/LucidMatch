"""
Custom exception classes for LucidMatch backend.
Provides structured error handling across the application.
"""

class LucidMatchError(Exception):
    """Base exception for all LucidMatch errors"""
    pass


class AgentError(LucidMatchError):
    """Base exception for agent-related errors"""
    pass


class ParserError(AgentError):
    """Raised when resume parsing fails"""
    pass


class ReasonerError(AgentError):
    """Raised when job matching fails"""
    pass


class AuditorError(AgentError):
    """Raised when bias audit fails"""
    pass


class StrategistError(AgentError):
    """Raised when curriculum generation fails"""
    pass


class ComparatorError(AgentError):
    """Raised when candidate comparison fails"""
    pass


class FileProcessingError(LucidMatchError):
    """Raised when file processing fails"""
    pass


class ValidationError(LucidMatchError):
    """Raised when input validation fails"""
    pass


class DatabaseError(LucidMatchError):
    """Raised when database operations fail"""
    pass
