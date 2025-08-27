import asyncio
import logging

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.auth import User, api_key_auth, get_current_active_user, rate_limit_check

# Importa router e dependências reais
from app.web.routes import router

# Silenciar logs desnecessários nos testes
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("anyio").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


# === Mock leve/instantâneo da IA ===
class DummyAIProvider:
    async def classify(self, text: str):
        await asyncio.sleep(0)  # yield ao loop, mas sem travar
        return {
            "category": "Produtivo",
            "confidence": 0.97,
            "rationale": "Texto mockado para testes",
            "meta": {"model": "mock-gpt-4o-mini", "cost": 0.0, "fallback": False},
        }

    async def generate_reply(self, text: str, category: str, tone: str):
        await asyncio.sleep(0)
        tone_emoji = {"formal": "", "neutro": "", "amigavel": "😊"}
        return f"Prezado(a), recebemos sua solicitação sobre {category}. {tone_emoji.get(tone, '')}"

    async def refine_reply(self, text: str, tone: str):
        await asyncio.sleep(0)
        return f"[{tone}] {text.strip()}"


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    app = FastAPI(title="Test Email Classifier")
    app.include_router(router)

    # === Overrides simples e diretos ===
    async def _current_user():
        return User(username="test_user", scopes=["classify:read"], disabled=False)

    async def _api_key_ok():
        return "test-mock-api-key-not-real"

    async def _rate_limit_ok():
        return True

    # Sobrescreve as dependências diretamente
    app.dependency_overrides[get_current_active_user] = _current_user
    app.dependency_overrides[api_key_auth] = _api_key_ok
    app.dependency_overrides[rate_limit_check] = _rate_limit_ok

    # === Injeta o provedor de IA "fake" ===
    import app.services.ai as ai_module

    ai_module.ai_provider = DummyAIProvider()

    return app


@pytest.fixture
async def client(test_app: FastAPI):
    """Cliente HTTP com timeout explícito"""
    # Timeout explícito para evitar pendurar
    async with AsyncClient(
        app=test_app, base_url="http://test", timeout=5.0, follow_redirects=True
    ) as c:
        yield c


# Fixture para arquivos de teste pequenos
@pytest.fixture
def sample_txt_file():
    """Arquivo TXT pequeno para testes"""
    return ("test.txt", b"Preciso de suporte urgente com o sistema", "text/plain")


@pytest.fixture
def sample_pdf_content():
    """Conteúdo PDF mínimo para testes (não é um PDF real, mas passa na validação mock)"""
    return b"%PDF-1.4\nPreciso de ajuda com o sistema\n%%EOF"


@pytest.fixture
def large_file_content():
    """Arquivo grande para testar limite de tamanho"""
    return b"a" * (3 * 1024 * 1024)  # 3MB
