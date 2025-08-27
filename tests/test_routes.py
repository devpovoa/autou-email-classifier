import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_index_page():
    """Test main page renders"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_classify_empty_text():
    """Test classification with empty text"""
    response = client.post("/classify", data={"text": "", "tone": "neutro"})
    assert response.status_code == 400
    error = response.json()
    assert "nenhum texto ou arquivo" in error["detail"].lower()


def test_classify_too_long_text():
    """Test classification with text exceeding limit"""
    long_text = "a" * 6000  # Exceeds 5000 char limit
    response = client.post(
        "/classify", data={"text": long_text, "tone": "neutro"}
    )
    assert response.status_code == 400
    error = response.json()
    assert "limite" in error["detail"].lower()


def test_classify_valid_productive_text():
    """Test classification with valid productive text"""
    text = "Preciso de ajuda com um problema no sistema de login. Erro 404."
    response = client.post("/classify", data={"text": text, "tone": "neutro"})

    # Should succeed (even with fallback)
    if response.status_code == 200:
        data = response.json()
        assert "category" in data
        assert "confidence" in data
        assert "reply" in data
        assert "rationale" in data
        assert "latency_ms" in data
        assert data["category"] in ["Produtivo", "Improdutivo"]
        assert 0.0 <= data["confidence"] <= 1.0
    else:
        # If AI provider fails, should still return error gracefully
        assert response.status_code in [400, 500]


def test_classify_valid_improdutive_text():
    """Test classification with valid improdutive text"""
    text = "Parabéns pelo excelente trabalho! Muito obrigado por tudo."
    response = client.post("/classify", data={"text": text, "tone": "formal"})

    # Should succeed (even with fallback)
    if response.status_code == 200:
        data = response.json()
        assert data["category"] in ["Produtivo", "Improdutivo"]


def test_classify_different_tones():
    """Test classification with different tones"""
    text = "Preciso de ajuda com o sistema"

    for tone in ["formal", "neutro", "amigavel"]:
        response = client.post("/classify", data={"text": text, "tone": tone})
        # Should not fail due to tone
        assert response.status_code in [200, 500]  # 500 if AI provider fails


def test_refine_empty_text():
    """Test refinement with empty text"""
    response = client.post("/refine", json={"text": "", "tone": "formal"})
    assert response.status_code == 400
    error = response.json()
    assert "muito curto" in error["detail"].lower()


def test_refine_valid_text():
    """Test refinement with valid text"""
    text = "Obrigado pelo contato. Vamos analisar sua solicitação."
    response = client.post("/refine", json={"text": text, "tone": "amigavel"})

    # Should succeed or fail gracefully
    if response.status_code == 200:
        data = response.json()
        assert "reply" in data
        assert "latency_ms" in data
        assert len(data["reply"]) > 0
    else:
        assert response.status_code == 500


def test_classify_with_invalid_file():
    """Test classification with invalid file"""
    # Create a fake file
    fake_file = ("test.pdf", b"not a real pdf", "application/pdf")

    response = client.post(
        "/classify", data={"tone": "neutro"}, files={"file": fake_file}
    )

    assert response.status_code == 400


def test_classify_with_oversized_file():
    """Test classification with oversized file"""
    # Create a large fake file (over 2MB)
    large_content = b"a" * (3 * 1024 * 1024)  # 3MB
    fake_file = ("large.txt", large_content, "text/plain")

    response = client.post(
        "/classify", data={"tone": "neutro"}, files={"file": fake_file}
    )

    assert response.status_code == 400
    error = response.json()
    assert "muito grande" in error["detail"].lower()
