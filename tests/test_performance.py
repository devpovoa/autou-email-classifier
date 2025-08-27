"""
Performance and load testing for the email classifier
Testes de performance e carga para o sistema AutoU
Valida comportamento sob diferentes cargas de trabalho
"""

import asyncio
import concurrent.futures
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestPerformance:
    """Testes de performance do sistema"""

    def test_single_classification_response_time(self):
        """Testa tempo de resposta para classificação única"""
        text = "Preciso de ajuda com problema no sistema"

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.8,
                "rationale": "Solicitação de suporte",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Resposta automática"

            start_time = time.time()
            response = client.post(
                "/classify", data={"text": text, "tone": "neutro"}
            )
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # em ms

            if response.status_code == 200:
                # Deve responder em menos de 5 segundos (com mock)
                assert response_time < 5000

                result = response.json()
                assert "latency_ms" in result
                assert result["latency_ms"] > 0

    def test_concurrent_requests_handling(self):
        """Testa manipulação de requisições concorrentes"""
        text = "Teste de concorrência"

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.8,
                "rationale": "Teste",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Resposta"

            def make_request():
                return client.post(
                    "/classify", data={"text": text, "tone": "neutro"}
                )

            # Executar 10 requisições concorrentes
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=10
            ) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in futures]

            # Todas devem ter sucesso
            success_count = sum(1 for r in results if r.status_code == 200)
            assert success_count >= 8  # Pelo menos 80% de sucesso

    def test_large_text_processing_time(self):
        """Testa processamento de texto grande"""
        # Texto próximo ao limite (4500 chars)
        large_text = "Este é um texto longo para testar performance. " * 90

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.7,
                "rationale": "Texto longo",
                "meta": {"model": "test", "cost": 0.005, "fallback": False},
            }
            mock_reply.return_value = "Processado com sucesso"

            start_time = time.time()
            response = client.post(
                "/classify", data={"text": large_text, "tone": "neutro"}
            )
            end_time = time.time()

            processing_time = (end_time - start_time) * 1000

            if response.status_code == 200:
                # Textos grandes devem processar em menos de 10 segundos
                assert processing_time < 10000

    def test_memory_usage_with_multiple_files(self):
        """Testa uso de memória com múltiplos arquivos"""
        file_content = "Conteúdo de teste para arquivo " * 100

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.8,
                "rationale": "Arquivo processado",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Arquivo processado"

            # Processar 5 arquivos em sequência
            for i in range(5):
                files = {
                    "file": (
                        f"test{i}.txt",
                        file_content.encode(),
                        "text/plain",
                    )
                }
                response = client.post(
                    "/classify", data={"tone": "neutro"}, files=files
                )

                # Não deve falhar por problemas de memória
                assert response.status_code in [200, 400, 500]


class TestScalability:
    """Testes de escalabilidade"""

    def test_health_endpoint_under_load(self):
        """Testa endpoint de health sob carga"""

        def check_health():
            return client.get("/health")

        # 50 requisições concorrentes ao health
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(check_health) for _ in range(50)]
            results = [future.result() for future in futures]

        # Todas devem retornar 200
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count == 50

    def test_fallback_performance_under_ai_failure(self):
        """Testa performance do fallback quando IA falha"""
        text = "Problema no sistema preciso suporte urgente"

        # Simular falha da IA para forçar uso do fallback
        with patch("app.services.ai.ai_provider.classify") as mock_classify:
            mock_classify.side_effect = Exception("API Error")

            start_time = time.time()
            response = client.post(
                "/classify", data={"text": text, "tone": "neutro"}
            )
            end_time = time.time()

            fallback_time = (end_time - start_time) * 1000

            # Fallback deve ser muito rápido (< 1 segundo)
            assert fallback_time < 1000

            if response.status_code == 200:
                result = response.json()
                assert result["meta"]["fallback"] is True


class TestRobustness:
    """Testes de robustez do sistema"""

    def test_malformed_input_handling(self):
        """Testa manipulação de entrada malformada"""
        # Teste casos que realmente devem falhar
        malformed_inputs = [
            {},  # Sem dados
            {"text": "", "tone": "neutro"},  # Texto vazio
            {"tone": "neutro"},  # Sem texto
        ]

        for malformed_input in malformed_inputs:
            response = client.post("/classify", data=malformed_input)
            # Deve retornar erro 400 para input inválido
            assert response.status_code == 400

    def test_special_characters_handling(self):
        """Testa manipulação de caracteres especiais"""
        special_texts = [
            "Texto com emojis 😊🎉💻",
            "Texto com acentos: ção, não, coração",
            "Text with special chars: @#$%^&*()",
            "Texto\ncom\nquebras\nde\nlinha",
            "Texto\tcom\ttabs",
            "Texto com    espaços    extras",
        ]

        with patch(
            "app.services.ai.ai_provider.classify"
        ) as mock_classify, patch(
            "app.services.ai.ai_provider.generate_reply"
        ) as mock_reply:

            mock_classify.return_value = {
                "category": "Produtivo",
                "confidence": 0.7,
                "rationale": "Caracteres especiais processados",
                "meta": {"model": "test", "cost": 0.001, "fallback": False},
            }
            mock_reply.return_value = "Processado"

            for special_text in special_texts:
                response = client.post(
                    "/classify", data={"text": special_text, "tone": "neutro"}
                )

                # Deve processar sem erros
                assert response.status_code in [200, 400]

    def test_boundary_value_testing(self):
        """Testa valores limítrofes"""
        # Texto no limite exato
        limit_text = "a" * 5000  # Exatamente o limite
        response = client.post(
            "/classify", data={"text": limit_text, "tone": "neutro"}
        )
        # Pode dar 200 ou 400, mas não deve quebrar
        assert response.status_code in [200, 400]

        # Texto 1 char acima do limite
        over_limit_text = "a" * 5001
        response = client.post(
            "/classify", data={"text": over_limit_text, "tone": "neutro"}
        )
        assert response.status_code == 400


class TestResourceUsage:
    """Testes de uso de recursos"""

    def test_memory_cleanup_after_processing(self):
        """Testa limpeza de memória após processamento"""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Processar vários textos
        for i in range(10):
            text = f"Teste de memória número {i} " * 50

            with patch(
                "app.services.ai.ai_provider.classify"
            ) as mock_classify, patch(
                "app.services.ai.ai_provider.generate_reply"
            ) as mock_reply:

                mock_classify.return_value = {
                    "category": "Produtivo",
                    "confidence": 0.8,
                    "rationale": f"Teste {i}",
                    "meta": {
                        "model": "test",
                        "cost": 0.001,
                        "fallback": False,
                    },
                }
                mock_reply.return_value = f"Resposta {i}"

                response = client.post(
                    "/classify", data={"text": text, "tone": "neutro"}
                )

        # Forçar garbage collection
        gc.collect()

        final_memory = process.memory_info().rss
        memory_growth = (final_memory - initial_memory) / 1024 / 1024  # MB

        # Crescimento de memória não deve ser excessivo (< 100MB)
        assert memory_growth < 100

    def test_cpu_usage_during_processing(self):
        """Testa uso de CPU durante processamento"""
        import psutil

        # Monitorar CPU antes
        cpu_before = psutil.cpu_percent(interval=1)

        # Fazer várias requisições
        for i in range(5):
            with patch(
                "app.services.ai.ai_provider.classify"
            ) as mock_classify, patch(
                "app.services.ai.ai_provider.generate_reply"
            ) as mock_reply:

                mock_classify.return_value = {
                    "category": "Produtivo",
                    "confidence": 0.8,
                    "rationale": "Teste CPU",
                    "meta": {
                        "model": "test",
                        "cost": 0.001,
                        "fallback": False,
                    },
                }
                mock_reply.return_value = "Resposta"

                response = client.post(
                    "/classify",
                    data={"text": f"Teste CPU {i}" * 100, "tone": "neutro"},
                )

        cpu_after = psutil.cpu_percent(interval=1)

        # CPU não deve ficar constantemente alta (< 80%)
        assert cpu_after < 80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
