import pytest

from app.services.heuristics import (classify_heuristic,
                                     get_classification_confidence)


def test_classify_heuristic():
    """Test heuristic classification"""
    # Test productive email
    productive_text = """
    Olá, estou com um problema no sistema de acesso.
    Meu usuário não consegue fazer login e preciso de suporte urgente.
    Protocolo: 12345
    """
    category, confidence, rationale = classify_heuristic(productive_text)
    assert category == "Produtivo"
    assert confidence > 0.5
    assert "termos" in rationale.lower()

    # Test improdutive email
    improdutive_text = """
    Parabéns pela excelente apresentação!
    Gostaria de agradecer pelo ótimo trabalho.
    """
    category, confidence, rationale = classify_heuristic(improdutive_text)
    assert category == "Improdutivo"

    # Test short text
    short_text = "Oi"
    category, confidence, rationale = classify_heuristic(short_text)
    assert category == "Improdutivo"
    assert "muito curto" in rationale.lower()

    # Test empty text
    category, confidence, rationale = classify_heuristic("")
    assert category == "Improdutivo"
    assert confidence == 0.5


def test_get_classification_confidence():
    """Test confidence calculation"""
    # Test with keywords
    text = "Preciso de suporte para resolver um problema urgente"
    confidence = get_classification_confidence("Produtivo", text)
    assert 0.5 <= confidence <= 0.9

    # Test with empty text
    confidence = get_classification_confidence("Produtivo", "")
    assert confidence == 0.5

    # Test with long text
    long_text = "a" * 2000
    confidence = get_classification_confidence("Produtivo", long_text)
    assert confidence > 0.5
