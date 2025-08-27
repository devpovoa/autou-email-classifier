import re
from typing import List

from app.core.logger import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text for processing"""
    if not text:
        return ""

    # Remove email headers (line by line)
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        # Skip header lines
        if (
            line.startswith("De:")
            or line.startswith("Para:")
            or line.startswith("Assunto:")
            or line.startswith("Data:")
        ):
            continue
        # Skip signature separator but stop processing after it
        if re.match(r"^--+\s*$", line):
            break
        # Skip empty lines at the beginning
        if not line and not cleaned_lines:
            continue
        cleaned_lines.append(line)

    # Join lines and clean up
    result = " ".join(cleaned_lines)

    # Remove other footers
    result = re.sub(r"Enviado do meu.*$", "", result, flags=re.MULTILINE)

    # Normalize spaces
    result = re.sub(r"\s+", " ", result)

    return result.strip()


def preprocess_text(text: str) -> str:
    """Full text preprocessing pipeline"""
    try:
        # Basic cleaning
        cleaned = clean_text(text)

        # Additional normalization
        cleaned = re.sub(r"[^\w\s\.,\!\?\-]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        logger.info(
            "Text preprocessed successfully",
            original_length=len(text),
            cleaned_length=len(cleaned),
        )

        return cleaned
    except Exception as e:
        logger.error("Error preprocessing text", error=str(e))
        return text


def extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords for classification"""
    if not text:
        return []

    # Define productive keywords with weights
    productive_keywords = [
        "suporte",
        "status",
        "chamado",
        "erro",
        "problema",
        "bug",
        "protocolo",
        "ticket",
        "urgente",
        "bloqueio",
        "acesso",
        "fatura",
        "cobrança",
        "pagamento",
        "prazo",
        "vencimento",
        "sistema",
        "funcionalidade",
        "recurso",
        "configuração",
        "dúvida",
        "informação",
        "esclarecimento",
        "solicitação",
    ]

    text_lower = text.lower()
    found_keywords = []

    for keyword in productive_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)

    return found_keywords


def detect_language(text: str) -> str:
    """Simple language detection for Portuguese content"""
    if not text:
        return "pt"

    # Simple Portuguese indicators
    pt_indicators = ["que", "para", "com", "não", "por", "uma", "seu", "sua"]
    text_lower = text.lower()

    count = sum(1 for indicator in pt_indicators if indicator in text_lower)

    return "pt" if count >= 2 else "unknown"
