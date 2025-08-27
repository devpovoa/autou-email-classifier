import io
from typing import Optional

from pypdf import PdfReader

from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """Extract text from PDF file content"""
    try:
        # Create a BytesIO object from file content
        pdf_file = io.BytesIO(file_content)

        # Create PDF reader
        reader = PdfReader(pdf_file)

        # Extract text from all pages
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Clean up extracted text
        text = text.strip()

        if not text:
            logger.warning("PDF contains no extractable text")
            return None

        logger.info(
            "PDF text extracted successfully",
            pages=len(reader.pages),
            text_length=len(text),
        )

        return text

    except Exception as e:
        logger.error("Error extracting text from PDF", error=str(e))
        return None


def validate_pdf(file_content: bytes) -> bool:
    """Validate if file content is a valid PDF"""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        # If we can read pages, it's valid
        len(reader.pages)
        return True
    except Exception:
        return False
