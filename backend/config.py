"""
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
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
