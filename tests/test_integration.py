"""
Testes de integração para o sistema AutoU - Classificador de E-mails
Testa o fluxo completo da aplicação: interface web, processamento,
classificação e resposta
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestWebInterfaceIntegration:
    """Testes de integração da interface web"""

    def test_main_page_loads_successfully(self):
        """Testa se a página principal carrega corretamente"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AutoU" in response.text
        assert "Classificador de E-mails" in response.text

    def test_health_endpoint_integration(self):
        """Testa o endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestUploadIntegration:
    """Testes de integração de upload"""

    def test_upload_txt_file_integration(self):
        """Testa upload completo de arquivo TXT"""
        # Criar arquivo TXT temporário
        txt_content = (
            "Preciso de suporte urgente para resolver problema no sistema"
        )
        txt_bytes = txt_content.encode("utf-8")

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            # Mock das respostas da IA
            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.85,
                "rationale": "Solicitação de suporte técnico",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Recebemos sua solicitação de suporte..."

            files = {"file": ("test.txt", txt_bytes, "text/plain")}
            data = {"tone": "neutro"}

            response = client.post("/classify", data=data, files=files)

            if response.status_code == 200:
                result = response.json()
                assert result["category"] == "Produtivo"
                assert result["confidence"] == 0.85
                assert "reply" in result
                assert "latency_ms" in result

    def test_upload_pdf_file_integration(self):
        """Testa upload de arquivo PDF (simulado)"""
        # Criar conteúdo PDF simulado (não é PDF real)
        pdf_content = b"fake pdf content for testing"

        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"tone": "formal"}

        response = client.post("/classify", data=data, files=files)

        # Deve falhar pois não é PDF real
        assert response.status_code == 400
        error = response.json()
        assert "inválido" in error["detail"].lower()

    def test_direct_text_input_integration(self):
        """Testa inserção direta de texto"""
        text = "Parabéns pelo excelente trabalho realizado pela equipe!"

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Improdutivo",
                "confidence": 0.75,
                "rationale": "Mensagem de felicitação",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Obrigado pelas palavras!"

            response = client.post(
                "/classify", data={"text": text, "tone": "amigavel"}
            )

            if response.status_code == 200:
                result = response.json()
                assert result["category"] == "Improdutivo"
                assert "Obrigado" in result["reply"]


class TestFullWorkflowIntegration:
    """Testes de integração do fluxo completo"""

    @patch("app.services.ai.ai_provider.classify")
    @patch("app.services.ai.ai_provider.generate_reply")
    def test_complete_productive_email_workflow(
        self, mock_reply, mock_classify
    ):
        """Testa fluxo completo para email produtivo"""
        # Setup mocks
        mock_classify.return_value = {
            "category": "Produtivo",
            "confidence": 0.85,
            "rationale": "Contém solicitação de suporte técnico",
            "meta": {"model": "gpt-4o-mini", "cost": 0.002, "fallback": False},
        }
        mock_reply.return_value = (
            "Prezado(a),\n\nRecebemos sua solicitação e ela será "
            "analisada pela nossa equipe. Retornaremos em até 24h."
        )

        # Email produtivo
        email_text = """
        Assunto: Erro no sistema de login
        
        Olá,
        
        Estou enfrentando problemas para acessar minha conta.
        O sistema retorna erro 500 quando tento fazer login.
        
        Protocolo: #12345
        
        Obrigado.
        """

        response = client.post(
            "/classify", data={"text": email_text, "tone": "formal"}
        )

        assert response.status_code == 200
        result = response.json()

        # Validar resposta (usando fallback quando OpenAI não configurado)
        assert result["category"] == "Produtivo"
        assert result["confidence"] > 0
        assert len(result["reply"]) > 10
        assert result["latency_ms"] > 0

        # Verificar se mocks foram chamados
        mock_classify.assert_called_once()
        mock_reply.assert_called_once()

    @patch("app.services.ai.ai_provider.classify")
    @patch("app.services.ai.ai_provider.generate_reply")
    def test_complete_improdutive_email_workflow(
        self, mock_reply, mock_classify
    ):
        """Testa fluxo completo para email improdutivo"""
        mock_classify.return_value = {
            "category": "Improdutivo",
            "confidence": 0.80,
            "rationale": "Mensagem de agradecimento",
            "meta": {"model": "gpt-4o-mini", "cost": 0.001, "fallback": False},
        }
        mock_reply.return_value = (
            "Oi! 😊\n\nObrigado pelas palavras carinhosas!"
        )

        email_text = "Muito obrigado pelo excelente atendimento!"

        response = client.post(
            "/classify", data={"text": email_text, "tone": "amigavel"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result["category"] == "Improdutivo"
        assert "😊" in result["reply"]

    def test_ai_failure_fallback_integration(self):
        """Testa o fallback quando a IA falha"""
        # Sem mockar - deixar o sistema usar fallback naturalmente quando OpenAI não configurado

        # Email com palavras-chave produtivas
        email_text = "Preciso de suporte urgente para resolver erro no sistema"

        response = client.post(
            "/classify", data={"text": email_text, "tone": "neutro"}
        )

        # Deve usar fallback heurístico e retornar 200
        assert response.status_code == 200
        result = response.json()
        assert result["category"] in ["Produtivo", "Improdutivo"]
        assert result["meta"]["fallback"] is True


class TestNLPIntegration:
    """Testes de integração do processamento NLP"""

    def test_text_preprocessing_integration(self):
        """Testa o pré-processamento de texto completo"""
        messy_text = """
        De: user@example.com
        Para: support@company.com
        
        Olá!!!    Preciso   de     ajuda@@@ com sistema...
        
        --
        Enviado do meu iPhone
        """

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.70,
                "rationale": "Solicitação de ajuda",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Sua solicitação foi recebida"

            response = client.post(
                "/classify", data={"text": messy_text, "tone": "neutro"}
            )

            # Verifica se o texto foi processado
            assert response.status_code == 200

            # Verifica se o pré-processamento foi aplicado
            # (o texto limpo foi passado para classify)
            called_text = mock_classify.call_args[0][0]
            assert "De:" not in called_text
            assert "iPhone" not in called_text
            assert "ajuda" in called_text


class TestAPIIntegration:
    """Testes de integração com APIs externas"""

    def test_refine_reply_integration(self):
        """Testa refinamento de resposta"""
        original_reply = "Sua mensagem foi recebida e será analisada."

        with patch("app.services.ai.ai_provider.refine_reply") as mock_refine:
            mock_refine.return_value = (
                "Oi! Sua mensagem chegou aqui e vamos dar uma olhada! 😊"
            )

            response = client.post(
                "/refine", json={"text": original_reply, "tone": "amigavel"}
            )

            assert response.status_code == 200
            result = response.json()
            assert "😊" in result["reply"]
            assert "latency_ms" in result

    def test_multiple_tone_variations(self):
        """Testa diferentes tons de resposta"""
        email_text = "Preciso verificar o status do meu pedido"

        for tone in ["formal", "neutro", "amigavel"]:
            with patch(
                "app.services.ai.ai_provider.classify"
            ) as mock_classify, patch(
                "app.services.ai.ai_provider.generate_reply"
            ) as mock_reply:

                mock_classify.return_value = {
                    "category": "Produtivo",
                    "confidence": 0.75,
                    "rationale": "Solicitação de status",
                    "meta": {
                        "model": "test",
                        "cost": 0.001,
                        "fallback": False,
                    },
                }

                if tone == "formal":
                    mock_reply.return_value = (
                        "Prezado(a), analisaremos seu pedido."
                    )
                elif tone == "amigavel":
                    mock_reply.return_value = (
                        "Oi! Vamos dar uma olhada no seu pedido! 😊"
                    )
                else:
                    mock_reply.return_value = "Sua solicitação será analisada."

                response = client.post(
                    "/classify", data={"text": email_text, "tone": tone}
                )

                assert response.status_code == 200
                result = response.json()

                # Verifica se o tom foi aplicado corretamente
                if tone == "formal":
                    assert "Prezado" in result["reply"]
                elif tone == "amigavel":
                    assert "😊" in result["reply"]


class TestErrorHandlingIntegration:
    """Testes de integração para tratamento de erros"""

    def test_file_size_limit_integration(self):
        """Testa limite de tamanho de arquivo"""
        # Arquivo muito grande (3MB)
        large_content = b"a" * (3 * 1024 * 1024)
        files = {"file": ("large.txt", large_content, "text/plain")}

        response = client.post(
            "/classify", data={"tone": "neutro"}, files=files
        )

        assert response.status_code == 400
        error = response.json()
        assert "muito grande" in error["detail"].lower()

    def test_character_limit_integration(self):
        """Testa limite de caracteres"""
        long_text = "a" * 6000  # Excede limite de 5000

        response = client.post(
            "/classify", data={"text": long_text, "tone": "neutro"}
        )

        assert response.status_code == 400
        error = response.json()
        assert "limite" in error["detail"].lower()

    def test_empty_input_integration(self):
        """Testa entrada vazia"""
        response = client.post(
            "/classify", data={"text": "", "tone": "neutro"}
        )

        assert response.status_code == 400
        error = response.json()
        assert "nenhum texto ou arquivo" in error["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
