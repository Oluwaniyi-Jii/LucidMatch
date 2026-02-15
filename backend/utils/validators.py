"""
Input validation utilities for LucidMatch.
"""
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from constants import MAX_FILE_SIZE_BYTES, ALLOWED_FILE_EXTENSIONS

logger = logging.getLogger(__name__)


async def validate_file_upload(file: UploadFile) -> bytes:
    """
    Validate uploaded file for size and type.
    
    Args:
        file: Uploaded file object
        
    Returns:
        File contents as bytes
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        logger.warning(f"Invalid file extension attempted: {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Read and check file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE_BYTES:
        logger.warning(f"File too large: {file_size} bytes")
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size / 1024 / 1024:.2f}MB). Maximum size: {MAX_FILE_SIZE_BYTES / 1024 / 1024}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    logger.info(f"File validation passed: {file.filename} ({file_size} bytes)")
    
    # Reset file pointer for future reads
    await file.seek(0)
    
    return contents


def validate_resume_text(text: str, max_length: int = 50000) -> None:
    """
    Validate extracted resume text.
    
    Args:
        text: Resume text content
        max_length: Maximum allowed text length
        
    Raises:
        HTTPException: If validation fails
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty")
    
    if len(text) > max_length:
        logger.warning(f"Resume text too long: {len(text)} characters")
        raise HTTPException(
            status_code=400,
            detail=f"Resume text too long ({len(text)} characters). Maximum: {max_length}"
        )
    
    logger.debug(f"Resume text validation passed: {len(text)} characters")
