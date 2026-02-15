"""
File processing utilities for handling uploads and text extraction.
"""
import logging
from io import BytesIO
from typing import Optional
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handles file upload processing and text extraction"""
    
    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """
        Extract text content from uploaded file.
        
        Supports:
        - PDF files (via pypdf)
        - Text files (UTF-8 encoded)
        
        Args:
            file: Uploaded file object
            
        Returns:
            Extracted text content
            
        Raises:
            FileProcessingError: If text extraction fails
        """
        from exceptions import FileProcessingError
        
        contents = await file.read()
        filename = file.filename.lower() if file.filename else ""
        
        # Handle PDF files
        if filename.endswith('.pdf'):
            return FileProcessor._extract_pdf_text(contents)
        
        # Handle text files
        else:
            return FileProcessor._extract_text_file(contents)
    
    @staticmethod
    def _extract_pdf_text(contents: bytes) -> str:
        """Extract text from PDF file"""
        from exceptions import FileProcessingError
        
        try:
            from pypdf import PdfReader
            
            pdf_file = BytesIO(contents)
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                logger.warning("PDF text extraction returned empty content")
                raise FileProcessingError("Unable to extract text from PDF. The PDF may be image-based or encrypted.")
            
            logger.info(f"Successfully extracted {len(text_content)} characters from PDF")
            return text_content
            
        except ImportError:
            logger.error("pypdf library not installed")
            raise FileProcessingError("PDF parsing library not available")
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise FileProcessingError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def _extract_text_file(contents: bytes) -> str:
        """Extract text from plain text file"""
        from exceptions import FileProcessingError
        
        try:
            text = contents.decode("utf-8")
            logger.info(f"Successfully decoded {len(text)} characters from text file")
            return text
        except UnicodeDecodeError as e:
            logger.error(f"Text file decoding failed: {e}")
            # Try with a more forgiving encoding
            try:
                text = contents.decode("latin-1")
                logger.warning("Had to use latin-1 encoding as fallback")
                return text
            except Exception:
                raise FileProcessingError("Unable to decode file content. Please ensure the file is UTF-8 encoded.")
