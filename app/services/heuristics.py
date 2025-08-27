from typing import Tuple

from app.core.logger import get_logger

logger = get_logger(__name__)


def classify_heuristic(text: str) -> Tuple[str, float, str]:
    """
    Fallback heuristic classification when AI provider fails
    Returns: (category, confidence, rationale)
    """
    if not text or len(text.strip()) < 10:
        return "Improdutivo", 0.5, "Texto muito curto para análise"

    text_lower = text.lower()

    # High-weight productive terms
    high_weight_terms = [
        "suporte",
        "chamado",
        "ticket",
        "protocolo",
        "erro",
        "bug",
        "problema",
        "falha",
        "urgente",
        "bloqueio",
        "travado",
        "status",
        "situação",
        "andamento",
        "prazo",
        "vencimento",
        "fatura",
        "cobrança",
        "pagamento",
        "débito",
        "crédito",
        "acesso",
        "senha",
        "login",
        "usuário",
        "permissão",
        "sistema",
        "plataforma",
        "funcionalidade",
        "recurso",
    ]

    # Medium-weight productive terms
    medium_weight_terms = [
        "dúvida",
        "pergunta",
        "informação",
        "esclarecimento",
        "solicitação",
        "pedido",
        "requisição",
        "configuração",
        "instalação",
        "atualização",
        "versão",
        "compatibility",
    ]

    # Low-weight terms (slightly productive)
    low_weight_terms = [
        "questão",
        "assunto",
        "tópico",
        "sobre",
        "referente",
        "preciso",
        "necessário",
        "importante",
        "ajuda",
    ]

    # Improdutive indicators
    improdutive_terms = [
        "parabéns",
        "felicitações",
        "agradecimento",
        "obrigado",
        "obrigada",
        "gratidão",
        "sucesso",
        "feliz",
        "satisfeito",
        "excelente",
        "ótimo",
        "bom trabalho",
        "bem feito",
    ]

    # Calculate scores
    high_score = sum(3 for term in high_weight_terms if term in text_lower)
    medium_score = sum(2 for term in medium_weight_terms if term in text_lower)
    low_score = sum(1 for term in low_weight_terms if term in text_lower)
    improdutive_score = sum(2 for term in improdutive_terms if term in text_lower)

    productive_score = high_score + medium_score + low_score

    # Text length bonus (longer texts are more likely to be productive)
    length_bonus = min(len(text) // 200, 2)
    productive_score += length_bonus

    # Decision logic
    if improdutive_score > productive_score:
        confidence = min(0.5 + (improdutive_score * 0.1), 0.85)
        rationale = (
            f"Contém {improdutive_score} termos indicativos de mensagem não-produtiva"
        )
        return "Improdutivo", confidence, rationale

    elif productive_score >= 3:
        confidence = min(0.6 + (productive_score * 0.05), 0.85)
        rationale = (
            f"Contém {productive_score} termos indicativos de necessidade de ação"
        )
        return "Produtivo", confidence, rationale

    elif productive_score >= 1:
        confidence = 0.55
        rationale = "Alguns indicadores de necessidade de ação identificados"
        return "Produtivo", confidence, rationale

    else:
        confidence = 0.5
        rationale = "Nenhum indicador claro identificado"
        return "Improdutivo", confidence, rationale


def get_classification_confidence(category: str, text: str) -> float:
    """Calculate confidence score based on text characteristics"""
    base_confidence = 0.5

    # Text length factor
    length_factor = min(len(text) / 1000, 0.2)

    # Keywords density
    keywords_found = len(
        [
            term
            for term in [
                "suporte",
                "problema",
                "erro",
                "ajuda",
                "dúvida",
                "status",
            ]
            if term in text.lower()
        ]
    )
    keyword_factor = min(keywords_found * 0.1, 0.3)

    return min(base_confidence + length_factor + keyword_factor, 0.9)
