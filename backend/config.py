"""
<<<<<<< HEAD
Centralized configuration module for LucidMatch backend.
Validates environment variables and provides typed configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment variables. "
        "Please create a .env file with ANTHROPIC_API_KEY=your-key-here"
    )

# Debug Mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:5174"
).split(",")

# Database
SQLITE_FILE_NAME = "lucidmatch.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

# Agent Configuration
PARSER_MAX_TOKENS = 1024
REASONER_MAX_TOKENS = 4096  # Increased for comprehensive evaluation
AUDITOR_MAX_TOKENS = 1024
STRATEGIST_MAX_TOKENS = 1024
COMPARATOR_MAX_TOKENS = 1024

# Model Configuration
DEFAULT_MODEL = "claude-opus-4-20250514"
=======
Configuration settings for LucidMatch backend
Loads environment variables and provides application settings
"""

import os
from dotenv import load_dotenv
from functools import lru_cache

# Load .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # API Keys (one is required)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # AI Model Configuration
        self.default_model = "claude-3-5-sonnet-20241022"  # or "gpt-4o"
        self.temperature = 0.3  # Lower for more consistent outputs
        self.max_tokens = 4096
        
        # Processing Settings
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
        self.privacy_mode = os.getenv("PRIVACY_MODE", "true").lower() == "true"
        self.bias_check_enabled = os.getenv("BIAS_CHECK_ENABLED", "true").lower() == "true"
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # Server Settings
        self.cors_origins = ["http://localhost:5173", "http://localhost:3000"]
    
    @property
    def ai_provider(self) -> str:
        """Determine which AI provider to use based on available keys"""
        if self.anthropic_api_key:
            return "anthropic"
        elif self.openai_api_key:
            return "openai"
        else:
            return "none"
    
    def validate_api_keys(self) -> bool:
        """Check if at least one API key is configured"""
        return bool(self.anthropic_api_key or self.openai_api_key)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
