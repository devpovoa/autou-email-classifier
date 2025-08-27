from typing import Optional

from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_txt(file_content: bytes) -> Optional[str]:
    """Extract text from TXT file content"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                text = file_content.decode(encoding)
                logger.info("TXT file decoded successfully",
                            encoding=encoding,
                            text_length=len(text))
                return text.strip()
            except UnicodeDecodeError:
                continue

        # If no encoding works
        logger.error("Could not decode TXT file with any encoding")
        return None

    except Exception as e:
        logger.error("Error extracting text from TXT file", error=str(e))
        return None


def validate_txt(file_content: bytes) -> bool:
    """Validate if file content is valid text"""
    try:
        # Try to decode as UTF-8
        file_content.decode('utf-8')
        return True
    except UnicodeDecodeError:
        # Try other encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                file_content.decode(encoding)
                return True
            except UnicodeDecodeError:
                continue
        return False
    except Exception:
        return False
