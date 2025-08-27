"""
Templates de prompts otimizados e sistema de few-shot learning
Demonstra ajuste e melhoria da IA através de engenharia de prompts
"""


class PromptTemplates:
    """Classe para gerenciar templates de prompts otimizados"""

    @staticmethod
    def get_classification_prompt_with_examples(text: str) -> str:
        """
        Prompt de classificação com exemplos few-shot para melhor precisão
        Simula 'treinamento' através de exemplos cuidadosamente selecionados
        """
        return f"""Tarefa: Classificar emails corporativos como "Produtivo" ou "Improdutivo".

DEFINIÇÕES:
- Produtivo: Requer ação/resposta (suporte técnico, dúvidas, problemas, solicitações, status, cobrança, acesso)
- Improdutivo: Não requer ação imediata (agradecimentos, felicitações, mensagens sociais)

EXEMPLOS DE TREINAMENTO:

Email: "Sistema está fora do ar desde ontem, preciso de ajuda urgente"
Classificação: {{"category": "Produtivo", "rationale": "Problema técnico urgente requer suporte imediato"}}

Email: "Parabéns pela apresentação excelente na reunião de hoje"
Classificação: {{"category": "Improdutivo", "rationale": "Mensagem de felicitação não requer ação"}}

Email: "Não consigo acessar minha conta, erro 403"
Classificação: {{"category": "Produtivo", "rationale": "Problema de acesso requer suporte técnico"}}

Email: "Obrigado pela ajuda de ontem, problema resolvido"
Classificação: {{"category": "Improdutivo", "rationale": "Agradecimento por problema já resolvido"}}

Email: "Qual o status do chamado #12345 aberto semana passada?"
Classificação: {{"category": "Produtivo", "rationale": "Solicitação de status de chamado requer informação"}}

Email: "Feliz aniversário! Desejo muito sucesso"
Classificação: {{"category": "Improdutivo", "rationale": "Mensagem social não requer resposta corporativa"}}

AGORA CLASSIFIQUE:
Email: \"\"\"{text}\"\"\"

Responda APENAS em JSON válido seguindo o formato dos exemplos:
{{"category":"Produtivo|Improdutivo","rationale":"<justificativa específica e objetiva>"}} """

    @staticmethod
    def get_reply_generation_prompt_enhanced(
        text: str, category: str, tone: str
    ) -> str:
        """
        Prompt melhorado para geração de respostas com contexto empresarial
        """
        tone_styles = {
            "formal": {
                "greeting": "Prezado(a)",
                "closing": "Atenciosamente,\nEquipe de Atendimento",
                "style": "linguagem formal e protocolar",
            },
            "neutro": {
                "greeting": "Olá",
                "closing": "Cordialmente,\nSuporte",
                "style": "linguagem clara e direta",
            },
            "amigavel": {
                "greeting": "Oi! 😊",
                "closing": "Um abraço,\nTime de Suporte",
                "style": "linguagem calorosa e próxima, com emojis apropriados",
            },
        }

        style_config = tone_styles.get(tone, tone_styles["neutro"])

        if category == "Produtivo":
            return f"""Contexto: Você é um especialista em atendimento ao cliente de uma empresa de tecnologia.

INSTRUÇÕES ESPECÍFICAS:
- Tom: {style_config['style']}
- Saudação: "{style_config['greeting']}"
- Encerramento: "{style_config['closing']}"

REGRAS PARA EMAILS PRODUTIVOS:
1. Reconheça especificamente o problema/solicitação
2. Informe próximos passos concretos
3. Solicite informações adicionais se necessário (protocolo, detalhes técnicos)
4. Estabeleça expectativa de prazo (24h úteis para análise inicial)
5. Mantenha 4-6 linhas, seja objetivo

EXEMPLOS DE BOM ATENDIMENTO:

Para problema técnico:
"{style_config['greeting']},
Identificamos o problema técnico relatado. Nossa equipe iniciará a análise imediatamente.
Para acelerar o processo, favor informar: sistema operacional, navegador e horário aproximado do erro.
Você receberá retorno em até 24h úteis com diagnóstico inicial.
{style_config['closing']}"

Para solicitação de acesso:
"{style_config['greeting']},
Sua solicitação de acesso foi recebida. Para prosseguir, precisamos validar algumas informações.
Envie por favor: cargo, departamento e justificativa do acesso solicitado.
O processo de liberação leva até 48h úteis após documentação completa.
{style_config['closing']}"

AGORA RESPONDA AO EMAIL:
\"\"\"{text}\"\"\""""

        else:  # Improdutivo
            return f"""Contexto: Você representa uma empresa que valoriza relacionamentos e reconhece mensagens positivas.

INSTRUÇÕES:
- Tom: {style_config['style']}
- Saudação: "{style_config['greeting']}"
- Encerramento: "{style_config['closing']}"

REGRAS PARA EMAILS IMPRODUTIVOS:
1. Reconheça e valorize a mensagem recebida
2. Demonstre que a mensagem foi importante
3. Reforce o relacionamento positivo
4. Encerre cordialmente sem criar expectativas
5. Mantenha 3-4 linhas, seja caloroso

EXEMPLOS DE BOA RESPOSTA:

Para agradecimento:
"{style_config['greeting']},
Ficamos muito felizes em saber que conseguimos ajudar! Seu feedback é muito importante para nós.
É um prazer ter você como cliente. Continue sempre à disposição para qualquer necessidade.
{style_config['closing']}"

Para felicitação:
"{style_config['greeting']},
Muito obrigado pelas palavras carinhosas! A equipe ficará muito contente com seu reconhecimento.
Mensagens como a sua motivam nosso trabalho diário. Agradecemos pela confiança!
{style_config['closing']}"

AGORA RESPONDA AO EMAIL:
\"\"\"{text}\"\"\""""

    @staticmethod
    def get_refinement_prompt_advanced(reply: str, tone: str) -> str:
        """
        Prompt avançado para refinamento com análise de qualidade
        """
        return f"""Tarefa: Analisar e melhorar resposta de atendimento ao cliente.

ANÁLISE REQUERIDA:
1. Verificar se o tom está adequado para: {tone}
2. Garantir clareza e objetividade
3. Manter profissionalismo
4. Ajustar comprimento (4-6 linhas ideais)

DIRETRIZES POR TOM:
- formal: linguagem protocolar, "Prezado(a)", "Atenciosamente"
- neutro: linguagem direta, "Olá", "Cordialmente"
- amigavel: linguagem calorosa, emojis sutis, "Oi!", "Um abraço"

TEXTO ATUAL:
\"\"\"{reply}\"\"\"

INSTRUÇÃO: Reescreva mantendo o sentido essencial mas ajustando para o tom "{tone}".
Responda APENAS com o texto melhorado, sem explicações."""

    @staticmethod
    def get_context_analysis_prompt(text: str) -> str:
        """
        Prompt para análise contextual avançada do email
        Ajuda a melhorar a precisão da classificação
        """
        return f"""Analise o contexto e características deste email para classificação precisa:

FATORES DE ANÁLISE:
1. Urgência (palavras como: urgente, imediato, crítico)
2. Tipo de solicitação (suporte, informação, acesso, cobrança)
3. Estado emocional (neutro, frustrado, satisfeito, preocupado)
4. Complexidade (simples, técnico, requer múltiplas etapas)
5. Histórico implícito (primeiro contato, follow-up, encerramento)

EMAIL:
\"\"\"{text}\"\"\"

ANÁLISE:
- Urgência: [baixa/média/alta]
- Tipo: [suporte/informacao/acesso/cobranca/social/outro]
- Emoção: [neutro/frustrado/satisfeito/preocupado]
- Complexidade: [simples/media/alta]
- Contexto: [primeiro_contato/follow_up/encerramento]

Baseado nesta análise, classifique como Produtivo ou Improdutivo e justifique."""


class PromptOptimizer:
    """Sistema para otimização contínua de prompts baseado em feedback"""

    def __init__(self):
        self.confidence_threshold = 0.7
        self.templates = PromptTemplates()

    def should_use_enhanced_prompt(self, text: str) -> bool:
        """
        Determina se deve usar prompt melhorado baseado na complexidade do texto
        """
        complexity_indicators = [
            len(text.split()) > 50,  # Texto longo
            any(
                word in text.lower()
                # Termos técnicos
                for word in ["protocolo", "chamado", "ticket"]
            ),
            text.count("?") > 1,  # Múltiplas perguntas
            any(
                word in text.lower() for word in ["urgente", "crítico", "imediato"]
            ),  # Urgência
        ]

        return sum(complexity_indicators) >= 2

    def get_optimized_classification_prompt(self, text: str) -> str:
        """
        Retorna o prompt otimizado baseado na complexidade do texto
        """
        if self.should_use_enhanced_prompt(text):
            return self.templates.get_classification_prompt_with_examples(text)
        else:
            # Prompt simplificado para casos básicos
            return f"""Classifique este email como "Produtivo" (requer ação) ou "Improdutivo" (não requer ação):

"{text}"

Responda em JSON: {{
                "category":"Produtivo|Improdutivo","rationale":"motivo"}} """

    def get_optimized_reply_prompt(self, text: str, category: str, tone: str) -> str:
        """
        Retorna prompt otimizado para geração de resposta
        """
        return self.templates.get_reply_generation_prompt_enhanced(text, category, tone)

    def analyze_response_quality(
        self, original_text: str, response: str, category: str
    ) -> dict:
        """
        Analisa qualidade da resposta para feedback e melhoria contínua
        """
        quality_metrics = {
            "length_appropriate": 50 <= len(response) <= 300,
            "addresses_request": any(
                word in response.lower() for word in original_text.lower().split()[:10]
            ),
            "has_next_steps": "será" in response
            or "prazo" in response
            or "retorno" in response,
            "professional_tone": not any(
                word in response.lower() for word in ["tchau", "beijo", "xoxo"]
            ),
            "category_appropriate": True,  # Simplificado para demo
        }

        quality_score = sum(quality_metrics.values()) / len(quality_metrics)

        return {
            "score": quality_score,
            "metrics": quality_metrics,
            "needs_improvement": quality_score < 0.8,
        }


# Instância global do otimizador
prompt_optimizer = PromptOptimizer()
