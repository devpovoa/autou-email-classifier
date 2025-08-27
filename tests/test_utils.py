import pytest

from app.utils.pdf import extract_text_from_pdf, validate_pdf
from app.utils.txt import extract_text_from_txt, validate_txt


def test_extract_text_from_txt():
    """Test text extraction from TXT content"""
    # Test UTF-8 text
    content = "Este é um texto de teste".encode('utf-8')
    result = extract_text_from_txt(content)
    assert result == "Este é um texto de teste"

    # Test Latin-1 text
    content = "Texto com acentuação".encode('latin-1')
    result = extract_text_from_txt(content)
    assert result is not None
    assert len(result) > 0

    # Test empty content
    result = extract_text_from_txt(b"")
    assert result == "" or result is None


def test_validate_txt():
    """Test TXT validation"""
    # Valid UTF-8
    content = "Texto válido".encode('utf-8')
    assert validate_txt(content) is True

    # Valid Latin-1
    content = "Texto com acentos".encode('latin-1')
    assert validate_txt(content) is True

    # Empty content
    assert validate_txt(b"") is True


def test_extract_text_from_pdf():
    """Test PDF text extraction (limited without actual PDF)"""
    # Test with invalid PDF content
    invalid_content = b"This is not a PDF"
    result = extract_text_from_pdf(invalid_content)
    assert result is None


def test_validate_pdf():
    """Test PDF validation"""
    # Test with invalid PDF content
    invalid_content = b"This is not a PDF"
    assert validate_pdf(invalid_content) is False

    # Test with empty content
    assert validate_pdf(b"") is False
