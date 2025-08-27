"""
Testes das melhorias de IA - Demonstra ajuste e otimização da IA
"""

import pytest

from app.services.ai import ai_provider
from app.services.prompt_templates import (PromptOptimizer, PromptTemplates,
                                           prompt_optimizer)


class TestPromptOptimization:
    """Testa otimização de prompts - demonstra 'treinamento' da IA"""

    def test_classification_prompt_with_examples(self):
        """Testa prompt com exemplos few-shot"""
        text = "Sistema está fora do ar, preciso de ajuda urgente"

        # Prompt básico vs melhorado
        basic_prompt = f'Classifique: "{text}"'
        enhanced_prompt = PromptTemplates.get_classification_prompt_with_examples(
            text)

        # Prompt melhorado deve ser mais detalhado
        assert len(enhanced_prompt) > len(basic_prompt) * 5
        assert "EXEMPLOS DE TREINAMENTO" in enhanced_prompt
        assert "few-shot" in enhanced_prompt or "exemplos" in enhanced_prompt.lower()

        # Deve conter exemplos específicos
        assert "Problema técnico urgente" in enhanced_prompt
        assert "Mensagem de felicitação" in enhanced_prompt

    def test_reply_generation_enhanced(self):
        """Testa geração de resposta melhorada"""
        text = "Não consigo acessar o sistema"

        for tone in ["formal", "neutro", "amigavel"]:
            prompt = PromptTemplates.get_reply_generation_prompt_enhanced(
                text, "Produtivo", tone
            )

            # Deve conter instruções específicas por tom
            # Para "neutro", o sistema usa "linguagem clara e direta"
            if tone == "neutro":
                assert "clara e direta" in prompt or "linguagem" in prompt.lower()
            else:
                assert tone in prompt.lower() or tone == "amigavel" and "calorosa" in prompt

            assert "INSTRUÇÕES ESPECÍFICAS" in prompt
            assert "EXEMPLOS DE BOM ATENDIMENTO" in prompt

    def test_prompt_optimizer_complexity_detection(self):
        """Testa detecção de complexidade para otimização"""
        optimizer = PromptOptimizer()

        # Texto simples
        simple_text = "Obrigado"
        assert not optimizer.should_use_enhanced_prompt(simple_text)

        # Texto complexo
        complex_text = "Preciso urgentemente de ajuda com o protocolo #12345, " \
            "pois o sistema crítico está fora do ar há 2 horas e " \
            "isso está impactando toda a operação"
        assert optimizer.should_use_enhanced_prompt(complex_text)

    def test_optimized_classification_prompt_selection(self):
        """Testa seleção automática de prompt otimizado"""
        optimizer = PromptOptimizer()

        # Texto simples - prompt básico
        simple_text = "Obrigado pela ajuda"
        simple_prompt = optimizer.get_optimized_classification_prompt(
            simple_text)
        assert len(simple_prompt) < 500  # Prompt mais simples

        # Texto complexo - prompt melhorado
        complex_text = "Sistema crítico fora do ar, protocolo urgente #12345"
        complex_prompt = optimizer.get_optimized_classification_prompt(
            complex_text)
        assert len(complex_prompt) > 1000  # Prompt com exemplos
        assert "EXEMPLOS DE TREINAMENTO" in complex_prompt

    def test_response_quality_analysis(self):
        """Testa análise de qualidade para melhoria contínua"""
        optimizer = PromptOptimizer()

        # Resposta boa
        good_response = ("Prezado(a), identificamos o problema relatado. "
                         "Nossa equipe iniciará análise em até 24h úteis. "
                         "Favor informar número do protocolo. Atenciosamente.")

        quality = optimizer.analyze_response_quality(
            "Problema no sistema", good_response, "Produtivo"
        )

        assert quality["score"] > 0.5
        assert isinstance(quality["metrics"], dict)
        assert "length_appropriate" in quality["metrics"]
        assert "professional_tone" in quality["metrics"]

        # Resposta ruim (muito curta)
        bad_response = "Ok"
        quality_bad = optimizer.analyze_response_quality(
            "Problema no sistema", bad_response, "Produtivo"
        )

        assert quality_bad["score"] < quality["score"]
        assert quality_bad["needs_improvement"] is True


class TestAITrainingDemonstration:
    """Demonstra processo de 'treinamento' através de engenharia de prompts"""

    def test_few_shot_learning_examples(self):
        """Testa exemplos few-shot como forma de 'treinar' a IA"""
        templates = PromptTemplates()

        # Deve conter múltiplos exemplos de treinamento
        prompt = templates.get_classification_prompt_with_examples("Teste")

        # Contar exemplos no prompt
        examples_count = prompt.count('Email: "')
        assert examples_count >= 6  # Pelo menos 6 exemplos

        # Cada exemplo deve ter classificação e justificativa
        classifications_count = prompt.count('"category":')
        assert classifications_count >= 6

        rationales_count = prompt.count('"rationale":')
        assert rationales_count >= 6

    def test_prompt_engineering_sophistication(self):
        """Testa sofisticação da engenharia de prompts"""
        # Prompt de classificação
        classification_prompt = PromptTemplates.get_classification_prompt_with_examples(
            "Teste")

        # Deve conter elementos avançados
        advanced_elements = [
            "DEFINIÇÕES:",
            "EXEMPLOS DE TREINAMENTO:",
            "AGORA CLASSIFIQUE:",
            "JSON válido",
            "rationale"
        ]

        for element in advanced_elements:
            assert element in classification_prompt

        # Prompt de resposta
        reply_prompt = PromptTemplates.get_reply_generation_prompt_enhanced(
            "Teste", "Produtivo", "formal"
        )

        # Deve conter instruções específicas
        reply_elements = [
            "INSTRUÇÕES ESPECÍFICAS:",
            "REGRAS PARA EMAILS",
            "EXEMPLOS DE BOM ATENDIMENTO:",
            "linguagem formal"
        ]

        for element in reply_elements:
            assert element in reply_prompt

    @pytest.mark.asyncio
    async def test_confidence_calculation_improvement(self):
        """Testa cálculo de confiança como métrica de qualidade"""
        # Simula classificação com alta confiança
        high_confidence_text = "Problema urgente no sistema, preciso de suporte técnico"
        result = {"category": "Produtivo",
                  "rationale": "Problema técnico claro que requer suporte imediato"}

        confidence = ai_provider._calculate_confidence(
            high_confidence_text, result)
        assert confidence > 0.7  # Alta confiança

        # Simula classificação com baixa confiança
        low_confidence_text = "Não sei bem o que dizer sobre isso"
        result_low = {"category": "Produtivo", "rationale": "Difícil"}

        confidence_low = ai_provider._calculate_confidence(
            low_confidence_text, result_low)
        assert confidence_low < confidence  # Confiança menor


class TestPromptVersioning:
    """Demonstra versionamento e evolução de prompts"""

    def test_prompt_evolution_tracking(self):
        """Testa que prompts evoluíram em complexidade"""
        # Prompt v1 (simples)
        v1_prompt = 'Classifique o email como "Produtivo" ou "Improdutivo"'

        # Prompt v2 (com exemplos)
        v2_prompt = PromptTemplates.get_classification_prompt_with_examples(
            "teste")

        # v2 deve ser significativamente mais complexo
        assert len(v2_prompt) > len(v1_prompt) * 10
        assert "exemplos" in v2_prompt.lower() or "examples" in v2_prompt.lower()

    def test_context_aware_prompting(self):
        """Testa prompts conscientes de contexto"""
        analyzer_prompt = PromptTemplates.get_context_analysis_prompt(
            "Sistema crítico fora do ar há 3 horas"
        )

        # Deve analisar múltiplos fatores
        context_factors = [
            "Urgência",
            "Tipo de solicitação",
            "Estado emocional",
            "Complexidade"
        ]

        for factor in context_factors:
            assert factor in analyzer_prompt


class TestContinuousImprovement:
    """Demonstra processo de melhoria contínua da IA"""

    def test_adaptive_prompt_selection(self):
        """Testa seleção adaptativa de prompts"""
        optimizer = prompt_optimizer

        # Casos diferentes devem usar prompts diferentes
        cases = [
            "Obrigado!",  # Simples
            "Preciso urgentemente resolver protocolo #12345 do sistema crítico",  # Complexo
        ]

        prompts = [optimizer.get_optimized_classification_prompt(
            case) for case in cases]

        # Prompts devem ser diferentes
        assert prompts[0] != prompts[1]
        assert len(prompts[1]) > len(prompts[0])  # Complexo deve ser maior

    def test_quality_metrics_tracking(self):
        """Testa rastreamento de métricas de qualidade"""
        optimizer = prompt_optimizer

        responses = [
            "Ok",  # Ruim
            "Prezado, recebemos sua solicitação e retornaremos em 24h com análise completa do protocolo informado. Cordialmente, Suporte",  # Boa
        ]

        qualities = []
        for response in responses:
            quality = optimizer.analyze_response_quality(
                "Problema no sistema", response, "Produtivo"
            )
            qualities.append(quality["score"])

        # Resposta melhor deve ter score maior
        assert qualities[1] > qualities[0]


if __name__ == "__main__":
    # Executar testes específicos de melhoria da IA
    pytest.main([__file__, "-v", "--tb=short"])
