import pytest


@pytest.mark.anyio
async def test_health_endpoint(client):
    """Teste endpoint de saúde"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.anyio
async def test_index_page(client):
    """Teste página principal"""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.anyio
async def test_classify_empty_text(client):
    """Teste classificação com texto vazio"""
    response = await client.post("/classify", data={"text": "", "tone": "neutro"})
    assert response.status_code == 400
    error = response.json()
    assert "nenhum texto ou arquivo" in error["detail"].lower()


@pytest.mark.anyio
async def test_classify_too_long_text(client):
    """Teste classificação com texto muito longo"""
    long_text = "a" * 6000  # Excede limite de 5000 chars
    response = await client.post(
        "/classify", data={"text": long_text, "tone": "neutro"}
    )
    assert response.status_code == 400
    error = response.json()
    assert "limite" in error["detail"].lower()


@pytest.mark.anyio
async def test_classify_valid_productive_text(client):
    """Teste classificação com texto produtivo válido"""
    text = "Preciso de ajuda com um problema no sistema de login. Erro 404."
    response = await client.post("/classify", data={"text": text, "tone": "neutro"})

    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "confidence" in data
    assert "reply" in data
    assert "rationale" in data
    assert "latency_ms" in data
    assert data["category"] in ["Produtivo", "Improdutivo"]
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.anyio
async def test_classify_valid_improdutive_text(client):
    """Teste classificação com texto improdutivo válido"""
    text = "Parabéns pelo excelente trabalho! Muito obrigado por tudo."
    response = await client.post("/classify", data={"text": text, "tone": "formal"})

    assert response.status_code == 200
    data = response.json()
    assert data["category"] in ["Produtivo", "Improdutivo"]


@pytest.mark.anyio
async def test_classify_single_tone(client):
    """Teste classificação com um tom (otimizado para não travar)"""
    text = "Preciso de ajuda com o sistema"

    response = await client.post("/classify", data={"text": text, "tone": "neutro"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] in ["Produtivo", "Improdutivo"]


@pytest.mark.anyio
async def test_refine_empty_text(client):
    """Teste refinamento com texto vazio"""
    response = await client.post("/refine", json={"text": "", "tone": "formal"})
    assert response.status_code == 400
    error = response.json()
    assert "muito curto" in error["detail"].lower()


@pytest.mark.anyio
async def test_refine_valid_text(client):
    """Teste refinamento com texto válido"""
    text = "Obrigado pelo contato. Vamos analisar sua solicitação."
    response = await client.post("/refine", json={"text": text, "tone": "amigavel"})

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "latency_ms" in data
    assert len(data["reply"]) > 0


@pytest.mark.anyio
async def test_classify_with_file_txt(client, sample_txt_file):
    """Teste classificação com arquivo TXT pequeno"""
    files = {"file": sample_txt_file}
    response = await client.post("/classify", data={"tone": "neutro"}, files=files)

    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert data["category"] in ["Produtivo", "Improdutivo"]


@pytest.mark.anyio
async def test_classify_with_oversized_file(client, large_file_content):
    """Teste classificação com arquivo muito grande"""
    fake_file = ("large.txt", large_file_content, "text/plain")
    files = {"file": fake_file}

    response = await client.post("/classify", data={"tone": "neutro"}, files=files)
    assert response.status_code == 400
    error = response.json()
    assert "muito grande" in error["detail"].lower()


# === Testes da API protegida (desabilitados temporariamente) ===
# Estes testes precisam de mocks mais complexos para require_scopes

# @pytest.mark.anyio
# async def test_classify_text_api(client):
#     """Teste API de classificação de texto (JWT protegida)"""
#     payload = {"text": "Quero suporte sobre minha conta", "tone": "neutro"}
#     response = await client.post("/api/classify/text", json=payload)
#
#     assert response.status_code == 200
#     data = response.json()
#     assert data["category"] == "Produtivo"  # Mock sempre retorna Produtivo
#     assert data["user"] == "test_user"
#     assert "timestamp" in data


# @pytest.mark.anyio
# async def test_classify_file_api(client, sample_txt_file):
#     """Teste API de classificação de arquivo (JWT protegida)"""
#     files = {"file": sample_txt_file}
#     response = await client.post("/api/classify/file", files=files)
#
#     assert response.status_code == 200
#     data = response.json()
#     assert data["filename"] == "test.txt"
#     assert data["category"] == "Produtivo"
#     assert data["user"] == "test_user"


# @pytest.mark.anyio
# async def test_classify_with_api_key(client):
#     """Teste classificação com API key (legacy)"""
#     payload = {"text": "Texto de teste", "tone": "neutro"}
#     response = await client.post("/api/v1/classify", json=payload)
#
#     assert response.status_code == 200
#     data = response.json()
#     assert data["category"] == "Produtivo"
#     assert data["auth_method"] == "api_key"
#     assert "timestamp" in data
