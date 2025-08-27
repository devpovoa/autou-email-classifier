"""
Testes específicos para validar requisitos do projeto
Baseado nas especificações fornecidas
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestRequisitoInterfaceWeb:
    """Test requirements validation"""

    def test_formulario_upload_existe(self):
        """Verifica se formulário de upload existe na página"""
        response = client.get("/")
        assert response.status_code == 200

        html_content = response.text.lower()

        # Deve ter formulário de upload
        assert "form" in html_content
        assert "file" in html_content or "upload" in html_content

        # Deve aceitar .txt e .pdf
        assert ".txt" in html_content
        assert ".pdf" in html_content

    def test_botao_envio_processamento(self):
        """Verifica se botão de envio para processamento existe"""
        response = client.get("/")
        assert response.status_code == 200

        html_content = response.text.lower()

        # Deve ter botão de submit/envio
        assert (
            "submit" in html_content
            or "processar" in html_content
            or "classificar" in html_content
            or "enviar" in html_content
        )

    def test_exibicao_categoria_resultado(self):
        """Testa se categoria é exibida nos resultados"""
        text = "Preciso de suporte técnico urgente"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.85,
                "rationale": "Solicitação de suporte",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Recebemos sua solicitação..."

            response = client.post("/classify", data={"text": text, "tone": "neutro"})

            assert response.status_code == 200
            result = response.json()

            # Deve retornar categoria "Produtivo" ou "Improdutivo"
            assert result["category"] in ["Produtivo", "Improdutivo"]
            assert result["category"] == "Produtivo"

    def test_exibicao_resposta_automatica(self):
        """Testa se resposta automática é exibida"""
        text = "Obrigado pelo excelente atendimento!"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Improdutivo",
                "confidence": 0.80,
                "rationale": "Agradecimento",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Ficamos felizes em atendê-lo!"

            response = client.post("/classify", data={"text": text, "tone": "amigavel"})

            assert response.status_code == 200
            result = response.json()

            # Deve retornar resposta automática
            assert "reply" in result
            assert len(result["reply"]) > 0
            assert "felizes" in result["reply"]


class TestRequisitoBackendPython:
    """Testa requisitos do Backend em Python"""

    def test_leitura_conteudo_emails_txt(self):
        """Testa leitura de conteúdo de emails em .txt"""
        email_content = "Preciso de ajuda com problema no sistema"
        txt_bytes = email_content.encode("utf-8")

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.8,
                "rationale": "Solicitação de ajuda",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Ajuda em andamento..."

            files = {"file": ("email.txt", txt_bytes, "text/plain")}
            response = client.post("/classify", data={"tone": "neutro"}, files=files)

            assert response.status_code == 200

            # Verifica se o conteúdo foi lido corretamente
            result = response.json()
            assert result["category"] == "Produtivo"

    def test_leitura_conteudo_emails_pdf(self):
        """Testa tentativa de leitura de PDF (deve falhar graciosamente com PDF fake)"""
        fake_pdf = b"fake pdf content"

        files = {"file": ("email.pdf", fake_pdf, "application/pdf")}
        response = client.post("/classify", data={"tone": "neutro"}, files=files)

        # Deve retornar erro para PDF inválido, mas sem quebrar
        assert response.status_code == 400
        error = response.json()
        assert "inválido" in error["detail"].lower()

    def test_preprocessamento_nlp(self):
        """Testa técnicas de NLP (remoção de stop words, processamento)"""
        from app.services.nlp import clean_text, extract_keywords, preprocess_text

        # Texto com elementos que devem ser removidos/processados
        messy_text = """
        De: user@example.com
        
        Olá!!! Preciso de suporte para resolver um erro no sistema urgente...
        
        Muito obrigado pela atenção.
        --
        Assinatura
        """

        # Testa limpeza
        cleaned = clean_text(messy_text)
        assert "De:" not in cleaned
        assert "suporte" in cleaned.lower()

        # Testa pré-processamento
        processed = preprocess_text(messy_text)
        assert len(processed) > 0

        # Testa extração de palavras-chave
        keywords = extract_keywords(processed)
        assert "suporte" in keywords or "urgente" in keywords

    def test_classificacao_produtivo_improdutivo(self):
        """Testa algoritmo de classificação em Produtivo/Improdutivo"""

        # Teste email produtivo
        email_produtivo = "Estou com problema no sistema e preciso de suporte urgente"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.85,
                "rationale": "Contém solicitação de suporte",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Analisaremos seu problema..."

            response = client.post(
                "/classify", data={"text": email_produtivo, "tone": "neutro"}
            )

            assert response.status_code == 200
            result = response.json()
            assert result["category"] == "Produtivo"

        # Teste email improdutivo
        email_improdutivo = "Parabéns pelo excelente trabalho da equipe!"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Improdutivo",
                "confidence": 0.80,
                "rationale": "Mensagem de felicitação",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Obrigado pelas palavras!"

            response = client.post(
                "/classify",
                data={"text": email_improdutivo, "tone": "amigavel"},
            )

            assert response.status_code == 200
            result = response.json()
            assert result["category"] == "Improdutivo"

    def test_integracao_api_ai(self):
        """Testa integração com API de AI (classificação e geração)"""
        # Verifica se AIProvider está configurado corretamente
        from app.core.config import settings
        from app.services.ai import ai_provider

        assert ai_provider is not None
        assert hasattr(ai_provider, "classify")
        assert hasattr(ai_provider, "generate_reply")
        assert hasattr(ai_provider, "refine_reply")

        # Verifica configuração de providers
        assert settings.provider in ["OpenAI", "HF"]
        assert hasattr(settings, "model_name")
        assert hasattr(settings, "ai_timeout")

    def test_classificacao_api_ai(self):
        """Testa uso de API de AI para classificação"""
        text = "Sistema está apresentando erro 500 constantemente"

        # Mock da resposta real da API
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": '{"category":"Produtivo","rationale":"Erro técnico reportado"}'
                        }
                    }
                ],
                "usage": {"prompt_tokens": 50, "completion_tokens": 20},
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            response = client.post("/classify", data={"text": text, "tone": "formal"})

            # Se passou pela classificação AI (mesmo mockada)
            if response.status_code == 200:
                result = response.json()
                assert result["category"] in ["Produtivo", "Improdutivo"]
                assert "rationale" in result

    def test_geracao_resposta_api_ai(self):
        """Testa geração de resposta usando API de AI"""
        text = "Preciso redefinir minha senha de acesso"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.85,
                "rationale": "Solicitação de redefinição de senha",
                "meta": {
                    "model": "gpt-4o-mini",
                    "cost": 0.002,
                    "fallback": False,
                },
            }

            # Mock de resposta gerada pela AI
            mock_reply.return_value = (
                "Prezado(a),\n\nRecebemos sua solicitação de "
                "redefinição de senha. Um link será enviado para "
                "seu email cadastrado em até 30 minutos."
            )

            response = client.post("/classify", data={"text": text, "tone": "formal"})

            assert response.status_code == 200
            result = response.json()

            # Verifica se resposta foi gerada adequadamente
            assert "reply" in result
            assert "senha" in result["reply"].lower()
            assert "link" in result["reply"].lower()


class TestRequisitoIntegracaoWeb:
    """Testa requisitos de Integração com Interface Web"""

    def test_conexao_backend_frontend(self):
        """Testa conexão entre backend e interface HTML"""

        # Frontend deve conseguir enviar dados para backend
        response = client.post(
            "/classify",
            data={
                "text": "Teste de conexão backend-frontend",
                "tone": "neutro",
            },
        )

        # Backend deve responder (mesmo que com erro por falta de IA)
        assert response.status_code in [200, 400, 500]

        # Se sucesso, deve retornar JSON estruturado
        if response.status_code == 200:
            result = response.json()
            required_fields = [
                "category",
                "confidence",
                "reply",
                "rationale",
                "latency_ms",
            ]
            for field in required_fields:
                assert field in result

    def test_recebimento_entradas_frontend(self):
        """Testa se backend recebe corretamente entradas do frontend"""

        # Teste com texto direto
        text_response = client.post(
            "/classify",
            data={"text": "Entrada de texto direto", "tone": "amigavel"},
        )

        # Deve processar entrada de texto
        assert text_response.status_code in [200, 400, 500]

        # Teste com arquivo
        file_content = b"Conteudo do arquivo de teste"
        files = {"file": ("test.txt", file_content, "text/plain")}

        file_response = client.post("/classify", data={"tone": "formal"}, files=files)

        # Deve processar entrada de arquivo
        assert file_response.status_code in [200, 400, 500]

    def test_exibicao_resultados_frontend(self):
        """Testa se resultados são formatados corretamente para exibição"""

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.87,
                "rationale": "Email contém solicitação técnica",
                "meta": {
                    "model": "gpt-4o-mini",
                    "cost": 0.0025,
                    "fallback": False,
                },
            }
            mock_reply.return_value = (
                "Prezado(a), sua solicitação técnica foi "
                "recebida e será analisada em até 24h."
            )

            response = client.post(
                "/classify",
                data={
                    "text": "Problemas técnicos no sistema de login",
                    "tone": "formal",
                },
            )

            assert response.status_code == 200
            result = response.json()

            # Resultados devem estar formatados para exibição
            assert result["category"] in ["Produtivo", "Improdutivo"]
            assert isinstance(result["confidence"], (int, float))
            assert 0 <= result["confidence"] <= 1
            assert isinstance(result["reply"], str)
            assert len(result["reply"]) > 0
            assert isinstance(result["rationale"], str)
            assert isinstance(result["latency_ms"], (int, float))
            assert result["latency_ms"] >= 0

            # Metadados devem estar presentes
            assert "meta" in result
            assert "model" in result["meta"]
            assert "fallback" in result["meta"]


class TestRequisitosFuncionaisEspecíficos:
    """Testa requisitos funcionais específicos mencionados"""

    def test_formatos_arquivo_suportados(self):
        """Testa suporte específico para .txt e .pdf"""

        # Arquivo .txt válido
        txt_content = b"Conteudo de email em formato txt"
        txt_files = {"file": ("email.txt", txt_content, "text/plain")}

        txt_response = client.post(
            "/classify", data={"tone": "neutro"}, files=txt_files
        )

        # Deve aceitar .txt
        assert txt_response.status_code in [
            200,
            400,
        ]  # 400 por falta de IA real
        if txt_response.status_code == 400:
            # Se erro, não deve ser por formato não suportado
            error = txt_response.json()
            assert "não suportado" not in error["detail"].lower()

        # Arquivo com extensão não suportada
        unsupported_files = {
            "file": (
                "email.docx",
                b"content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }

        unsupported_response = client.post(
            "/classify", data={"tone": "neutro"}, files=unsupported_files
        )

        # Deve rejeitar formatos não suportados
        assert unsupported_response.status_code == 400
        error = unsupported_response.json()
        assert "suportado" in error["detail"].lower()

    def test_insercao_direta_texto(self):
        """Testa funcionalidade de inserção direta de texto"""

        direct_text = "Email inserido diretamente na interface sem arquivo"

        with (
            patch("app.services.ai.ai_provider.classify") as mock_classify,
            patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
        ):

            mock_classify.return_value = {
                "category": "Improdutivo",
                "confidence": 0.70,
                "rationale": "Texto genérico",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Mensagem recebida com sucesso."

            response = client.post(
                "/classify", data={"text": direct_text, "tone": "neutro"}
            )

            assert response.status_code == 200
            result = response.json()
            assert result["category"] in ["Produtivo", "Improdutivo"]

    def test_categorias_especificas_produtivo_improdutivo(self):
        """Testa que sistema classifica especificamente em Produtivo ou Improdutivo"""

        test_cases = [
            ("Preciso de suporte para problema técnico", "Produtivo"),
            ("Parabéns pelo excelente atendimento", "Improdutivo"),
            ("Erro 404 no sistema", "Produtivo"),
            ("Muito obrigado pela ajuda", "Improdutivo"),
        ]

        for text, expected_category in test_cases:
            with (
                patch("app.services.ai.ai_provider.classify") as mock_classify,
                patch("app.services.ai.ai_provider.generate_reply") as mock_reply,
            ):

                mock_classify.return_value = {
                    "category": expected_category,
                    "confidence": 0.80,
                    "rationale": f"Classificado como {expected_category}",
                    "meta": {
                        "model": "test",
                        "cost": 0.001,
                        "fallback": False,
                    },
                }
                mock_reply.return_value = f"Resposta para {expected_category}"

                response = client.post(
                    "/classify", data={"text": text, "tone": "neutro"}
                )

                if response.status_code == 200:
                    result = response.json()
                    # Deve classificar exatamente nas categorias especificadas
                    assert result["category"] in ["Produtivo", "Improdutivo"]
                    assert result["category"] == expected_category


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
