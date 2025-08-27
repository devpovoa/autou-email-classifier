import pytest

from app.services.nlp import (
    clean_text,
    detect_language,
    extract_keywords,
    preprocess_text,
)


@pytest.mark.asyncio
async def test_clean_text():
    """Test text cleaning functionality"""
    # Test basic cleaning
    text = "  Este é um teste   com espaços   extras  "
    result = clean_text(text)
    assert result == "Este é um teste com espaços extras"

    # Test empty text
    assert clean_text("") == ""
    assert clean_text("   ") == ""

    # Test email header removal
    text_with_headers = """De: user@example.com
Para: support@company.com
Assunto: Problema no sistema
Data: 2024-01-01

Este é o conteúdo real do email.
--
Assinatura automática"""

    cleaned = clean_text(text_with_headers)
    assert "De:" not in cleaned
    assert "Para:" not in cleaned
    assert "Assunto:" not in cleaned
    assert "Este é o conteúdo real do email." in cleaned


def test_preprocess_text():
    """Test full text preprocessing pipeline"""
    text = "Este é um teste!!! Com pontuação @#$ estranha..."
    result = preprocess_text(text)
    assert result is not None
    assert len(result) > 0
    # Should remove special characters but keep basic punctuation
    assert "@#$" not in result


def test_extract_keywords():
    """Test keyword extraction"""
    # Test productive text
    productive_text = "Preciso de suporte para resolver um erro no sistema urgente"
    keywords = extract_keywords(productive_text)
    assert "suporte" in keywords
    assert "erro" in keywords
    assert "urgente" in keywords

    # Test empty text
    assert extract_keywords("") == []

    # Test non-productive text
    non_productive = "Parabéns pelo excelente trabalho!"
    keywords = extract_keywords(non_productive)
    assert len(keywords) == 0


def test_detect_language():
    """Test language detection"""
    # Portuguese text
    pt_text = "Este é um texto em português com palavras que não são comuns"
    assert detect_language(pt_text) == "pt"

    # Empty text
    assert detect_language("") == "pt"

    # Unknown language
    unknown_text = "This is English text"
    result = detect_language(unknown_text)
    assert result in ["pt", "unknown"]
