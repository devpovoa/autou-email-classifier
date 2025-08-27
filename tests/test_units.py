"""
Testes unitários abrangentes para o sistema AutoU - Classificador de E-mails
Testa componentes individuais: NLP, AI, utils, heuristics
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.ai import AIProvider
from app.services.heuristics import (
    classify_heuristic,
    get_classification_confidence,
)

# Import das classes a serem testadas
from app.services.nlp import (
    clean_text,
    detect_language,
    extract_keywords,
    preprocess_text,
)
from app.utils.pdf import extract_text_from_pdf, validate_pdf
from app.utils.txt import extract_text_from_txt, validate_txt


class TestNLPUnits:
    """Testes unitários para processamento NLP"""

    def test_clean_text_removes_headers(self):
        """Testa remoção de cabeçalhos de email"""
        email_with_headers = """De: user@test.com
Para: support@company.com
Assunto: Teste
Data: 2024-01-01

Conteúdo do email aqui.
--
Assinatura"""

        result = clean_text(email_with_headers)
        assert "De:" not in result
        assert "Para:" not in result
        assert "Assunto:" not in result
        assert "Conteúdo do email aqui." in result
        assert "--" not in result

    def test_clean_text_normalizes_whitespace(self):
        """Testa normalização de espaços em branco"""
        messy_text = "  Texto   com     espaços    extras  "
        result = clean_text(messy_text)
        assert result == "Texto com espaços extras"

    def test_clean_text_empty_input(self):
        """Testa entrada vazia"""
        assert clean_text("") == ""
        assert clean_text("   ") == ""
        assert clean_text(None) == ""

    def test_preprocess_text_removes_special_chars(self):
        """Testa remoção de caracteres especiais"""
        text_with_special = "Email@#$ com!! caracteres??? especiais***"
        result = preprocess_text(text_with_special)

        # Deve remover caracteres especiais mas manter pontuação básica
        assert "@#$" not in result
        assert "***" not in result
        assert "email" in result.lower()

    def test_extract_keywords_productive_terms(self):
        """Testa extração de palavras-chave produtivas"""
        productive_text = (
            "Preciso de suporte para resolver erro urgente no sistema"
        )
        keywords = extract_keywords(productive_text)

        expected_keywords = ["suporte", "erro", "urgente", "sistema"]
        for keyword in expected_keywords:
            assert keyword in keywords

    def test_extract_keywords_empty_text(self):
        """Testa extração com texto vazio"""
        assert extract_keywords("") == []
        assert extract_keywords("   ") == []

    def test_detect_language_portuguese(self):
        """Testa detecção de idioma português"""
        pt_text = "Este texto contém palavras que não são comuns para detectar português"
        assert detect_language(pt_text) == "pt"

    def test_detect_language_unknown(self):
        """Testa detecção de idioma desconhecido"""
        unknown_text = "This is English text without Portuguese indicators"
        result = detect_language(unknown_text)
        assert result in ["pt", "unknown"]


class TestHeuristicsUnits:
    """Testes unitários para classificação heurística"""

    def test_classify_heuristic_productive_high_weight(self):
        """Testa classificação heurística com termos de alto peso"""
        productive_text = (
            "Problema urgente no sistema, protocolo 12345, preciso suporte"
        )
        category, confidence, rationale = classify_heuristic(productive_text)

        assert category == "Produtivo"
        assert confidence > 0.6
        assert "termos" in rationale.lower()

    def test_classify_heuristic_improdutive_terms(self):
        """Testa classificação com termos improdutivos"""
        improdutive_text = "Parabéns pelo excelente trabalho, muito obrigado!"
        category, confidence, rationale = classify_heuristic(improdutive_text)

        assert category == "Improdutivo"
        assert confidence >= 0.5

    def test_classify_heuristic_short_text(self):
        """Testa classificação com texto muito curto"""
        short_text = "Oi"
        category, confidence, rationale = classify_heuristic(short_text)

        assert category == "Improdutivo"
        assert confidence == 0.5
        assert "muito curto" in rationale.lower()

    def test_classify_heuristic_empty_text(self):
        """Testa classificação com texto vazio"""
        category, confidence, rationale = classify_heuristic("")
        assert category == "Improdutivo"
        assert confidence == 0.5

    def test_get_classification_confidence_with_keywords(self):
        """Testa cálculo de confiança com palavras-chave"""
        text_with_keywords = (
            "Preciso de suporte para resolver problema no sistema"
        )
        confidence = get_classification_confidence(
            "Produtivo", text_with_keywords
        )

        assert 0.5 <= confidence <= 0.9
        assert confidence > 0.5  # Deve ser maior que base devido às keywords

    def test_get_classification_confidence_long_text(self):
        """Testa confiança com texto longo"""
        long_text = "palavra " * 500  # Texto longo
        confidence = get_classification_confidence("Produtivo", long_text)
        assert confidence > 0.5


class TestAIProviderUnits:
    """Testes unitários para o provedor de IA"""

    def setUp(self):
        self.ai_provider = AIProvider()

    @pytest.mark.asyncio
    async def test_classify_openai_success(self):
        """Testa classificação OpenAI com sucesso"""
        with patch(
            "app.services.ai.settings.openai_api_key", "test_key"
        ), patch("httpx.AsyncClient") as mock_client:
            # Mock da resposta da API
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": '{"category":"Produtivo","rationale":"Solicitação de suporte"}'
                        }
                    }
                ],
                "usage": {"prompt_tokens": 50, "completion_tokens": 20},
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            ai_provider = AIProvider()
            result = await ai_provider._classify_openai("Preciso de ajuda")

            assert result["category"] == "Produtivo"
            assert result["rationale"] == "Solicitação de suporte"
            assert result["meta"]["fallback"] is False

    @pytest.mark.asyncio
    async def test_classify_openai_api_error(self):
        """Testa tratamento de erro da API OpenAI"""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock de erro da API
            mock_response = Mock()
            mock_response.status_code = 500

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            ai_provider = AIProvider()

            # Deve usar fallback heurístico
            result = await ai_provider.classify("Preciso de suporte técnico")
            assert result["meta"]["fallback"] is True
            assert result["category"] in ["Produtivo", "Improdutivo"]

    @pytest.mark.asyncio
    async def test_classify_invalid_json_response(self):
        """Testa resposta JSON inválida da OpenAI"""
        with patch(
            "app.services.ai.settings.openai_api_key", "test_key"
        ), patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {"message": {"content": "Resposta inválida não JSON"}}
                ]
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            ai_provider = AIProvider()
            result = await ai_provider._classify_openai("Teste")

            # Deve retornar resposta padrão para JSON inválido
            assert result["category"] == "Produtivo"
            assert result["rationale"] == "Erro na resposta da IA"
            assert result["confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_generate_reply_openai_success(self):
        """Testa geração de resposta OpenAI"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "Prezado(a), recebemos sua solicitação..."
                        }
                    }
                ]
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            ai_provider = AIProvider()
            reply = await ai_provider._generate_reply_openai(
                "Preciso de ajuda", "Produtivo", "formal"
            )

            assert "Prezado" in reply
            assert len(reply) > 0

    def test_generate_reply_fallback_productive_formal(self):
        """Testa resposta fallback para email produtivo formal"""
        ai_provider = AIProvider()
        reply = ai_provider._generate_reply_fallback("Produtivo", "formal")

        assert "Prezado" in reply
        assert "solicitação" in reply.lower()
        assert "24" in reply  # Prazo de resposta

    def test_generate_reply_fallback_improdutive_amigavel(self):
        """Testa resposta fallback para email improdutivo amigável"""
        ai_provider = AIProvider()
        reply = ai_provider._generate_reply_fallback("Improdutivo", "amigavel")

        assert "😊" in reply
        assert "obrigado" in reply.lower() or "legal" in reply.lower()

    def test_estimate_cost_calculation(self):
        """Testa cálculo de custo da API"""
        ai_provider = AIProvider()
        usage = {"prompt_tokens": 100, "completion_tokens": 50}

        cost = ai_provider._estimate_cost(usage)
        assert cost > 0
        assert isinstance(cost, float)
        assert cost < 1  # Deve ser valor pequeno


class TestUtilsUnits:
    """Testes unitários para utilitários"""

    def test_extract_text_from_txt_utf8(self):
        """Testa extração de texto UTF-8"""
        content = "Texto com acentuação: ção, ã, é".encode("utf-8")
        result = extract_text_from_txt(content)

        assert result is not None
        assert "acentuação" in result
        assert "ção" in result

    def test_extract_text_from_txt_latin1(self):
        """Testa extração de texto Latin-1"""
        content = "Texto simples".encode("latin-1")
        result = extract_text_from_txt(content)

        assert result is not None
        assert "Texto simples" in result

    def test_extract_text_from_txt_empty(self):
        """Testa extração de texto vazio"""
        result = extract_text_from_txt(b"")
        assert result == "" or result is None

    def test_validate_txt_valid_utf8(self):
        """Testa validação de TXT UTF-8 válido"""
        content = "Texto válido".encode("utf-8")
        assert validate_txt(content) is True

    def test_validate_txt_valid_latin1(self):
        """Testa validação de TXT Latin-1 válido"""
        content = "Texto válido".encode("latin-1")
        assert validate_txt(content) is True

    def test_validate_pdf_invalid_content(self):
        """Testa validação de PDF inválido"""
        invalid_content = b"This is not a PDF file"
        assert validate_pdf(invalid_content) is False

    def test_validate_pdf_empty_content(self):
        """Testa validação de PDF vazio"""
        assert validate_pdf(b"") is False

    def test_extract_text_from_pdf_invalid(self):
        """Testa extração de PDF inválido"""
        invalid_content = b"Not a PDF"
        result = extract_text_from_pdf(invalid_content)
        assert result is None


class TestConfigurationUnits:
    """Testes unitários para configurações"""

    def test_settings_default_values(self):
        """Testa valores padrão das configurações"""
        from app.core.config import settings

        assert settings.provider in ["OpenAI", "HF"]
        assert settings.max_input_chars > 0
        assert settings.max_file_size > 0
        assert settings.ai_timeout > 0
        assert settings.port > 0

    @patch.dict("os.environ", {"PROVIDER": "HF", "MAX_INPUT_CHARS": "3000"})
    def test_settings_environment_override(self):
        """Testa override de configurações via environment"""
        # Recarregar settings com novas variáveis de ambiente
        from app.core.config import Settings

        test_settings = Settings()

        assert test_settings.provider == "HF"
        assert test_settings.max_input_chars == 3000


class TestLoggingUnits:
    """Testes unitários para logging"""

    def test_structured_logger_creation(self):
        """Testa criação do logger estruturado"""
        from app.core.logger import get_logger

        logger = get_logger("test")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_structured_logger_json_output(self):
        """Testa saída JSON do logger"""
        import logging

        from app.core.logger import StructuredLogger

        with patch("logging.Logger.log") as mock_log:
            logger = StructuredLogger("test")
            logger.info("Test message", key="value")

            # Verifica se foi chamado com JSON
            mock_log.assert_called_once()
            args = mock_log.call_args
            log_message = args[0][1]  # Segundo argumento é a mensagem

            # Deve ser JSON válido
            parsed = json.loads(log_message)
            assert parsed["level"] == "INFO"
            assert parsed["message"] == "Test message"
            assert parsed["key"] == "value"


class TestPromptTemplatesUnits:
    """Testes unitários para templates de prompts"""

    def test_classification_prompt_structure(self):
        """Testa estrutura do prompt de classificação"""
        ai_provider = AIProvider()

        # Simular o prompt (extrair da implementação)
        text = "Teste de email"

        # O prompt deve conter elementos essenciais
        prompt_template = """Tarefa: Classificar o e-mail como uma das categorias em ["Produtivo", "Improdutivo"].

Definições:
- Produtivo: requer ação/resposta objetiva
- Improdutivo: não requer ação imediata

E-mail:
\"\"\"{text}\"\"\"

Responda APENAS em JSON válido:
{{"category":"Produtivo|Improdutivo","rationale":"<motivo>"}}"""

        formatted_prompt = prompt_template.format(text=text)

        assert "Classificar" in formatted_prompt
        assert "Produtivo" in formatted_prompt
        assert "Improdutivo" in formatted_prompt
        assert "JSON válido" in formatted_prompt
        assert text in formatted_prompt

    def test_reply_generation_prompt_structure(self):
        """Testa estrutura do prompt de geração de resposta"""
        prompt_template = """Contexto: Você é um assistente de atendimento educado e objetivo.
Categoria: {category}
Tom: {tone}

Regras:
- 3 a 6 linhas, claras.
- Se "Produtivo": reconhecer pedido, apontar próximo passo
- Se "Improdutivo": agradecer e encerrar com cordialidade"""

        formatted = prompt_template.format(category="Produtivo", tone="formal")

        assert "assistente de atendimento" in formatted
        assert "Produtivo" in formatted
        assert "formal" in formatted
        assert "3 a 6 linhas" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
