import json
import re
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.core.logger import get_logger
from app.services.heuristics import classify_heuristic
from app.services.prompt_templates import prompt_optimizer

logger = get_logger(__name__)


def _safe_json_loads(content: str) -> dict:
    """
    Safely parse JSON content from OpenAI response
    Handles cases where response is wrapped in markdown code blocks
    """
    try:
        # Remove possíveis blocos ```json ... ``` ou ```
        content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE)
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning(
            "Invalid JSON returned by OpenAI", extra={"raw_content": content}
        )
        return {"category": "Produtivo", "rationale": "Erro na resposta da IA"}


def _validate_openai_response(data: dict) -> str:
    """
    Validate OpenAI API response and extract content
    Raises exception if response is invalid
    """
    if "choices" not in data or not data["choices"]:
        logger.error("OpenAI API response missing choices", extra={"data": data})
        raise Exception(f"OpenAI API error: {data.get('error', 'unknown error')}")

    content = data["choices"][0]["message"]["content"]
    if not content:
        raise Exception("OpenAI API returned empty content")

    return content.strip()


class AIProvider:
    def __init__(self):
        self.timeout = settings.ai_timeout

    async def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify email using optimized prompts and confidence analysis
        """
        try:
            if settings.provider == "OpenAI":
                # Use optimized prompts
                prompt = prompt_optimizer.get_optimized_classification_prompt(text)
                result = await self._classify_openai_with_prompt(prompt)

                # Add quality analysis
                if result.get("category"):
                    result["confidence"] = self._calculate_confidence(text, result)

                return result

            elif settings.provider == "HF":
                return await self._classify_huggingface(text)
            else:
                raise ValueError(f"Unsupported provider: {settings.provider}")
        except Exception as e:
            logger.error(
                "AI classification failed",
                error=str(e),
                provider=settings.provider,
            )
            # Fallback to heuristics
            category, confidence, rationale = classify_heuristic(text)
            return {
                "category": category,
                "confidence": confidence,
                "rationale": rationale,
                "meta": {
                    "model": "heuristic_fallback",
                    "cost": 0.0,
                    "fallback": True,
                },
            }

    async def generate_reply(self, text: str, category: str, tone: str) -> str:
        """
        Generate automated reply using optimized prompts
        """
        try:
            if settings.provider == "OpenAI":
                # Use enhanced prompt system
                prompt = prompt_optimizer.get_optimized_reply_prompt(
                    text, category, tone
                )
                reply = await self._generate_reply_openai_with_prompt(prompt)

                # Analyze response quality
                quality = prompt_optimizer.analyze_response_quality(
                    text, reply, category
                )

                # Log quality metrics for improvement
                logger.info(f"Reply quality score: {quality['score']}")
                if quality["needs_improvement"]:
                    logger.warning(
                        "Reply quality below threshold, " "consider prompt refinement"
                    )

                return reply

            elif settings.provider == "HF":
                return await self._generate_reply_huggingface(text, category, tone)
            else:
                return self._generate_reply_fallback(category, tone)
        except Exception as e:
            logger.error("Reply generation failed", error=str(e))
            return self._generate_reply_fallback(category, tone)

    async def refine_reply(self, reply: str, tone: str) -> str:
        """Refine existing reply with new tone"""
        try:
            if settings.provider == "OpenAI":
                return await self._refine_reply_openai(reply, tone)
            elif settings.provider == "HF":
                return await self._refine_reply_huggingface(reply, tone)
            else:
                return reply  # Return original if provider not available
        except Exception as e:
            logger.error("Reply refinement failed", error=str(e))
            return reply

    async def _classify_openai(self, text: str) -> Dict[str, Any]:
        """OpenAI classification implementation"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Tarefa: Classificar o e-mail como uma das categorias em ["Produtivo", "Improdutivo"].

Definições:
- Produtivo: requer ação/resposta objetiva (suporte, status de caso, dúvida sobre sistema,
cobrança, acesso, faturamento, prazo).
- Improdutivo: não requer ação imediata (felicitações, agradecimentos, mensagens
genéricas).

E-mail:
\"\"\"{text}\"\"\"

Responda APENAS em JSON válido:
{{"category":"Produtivo|Improdutivo","rationale":"<motivo curto objetivo>"}} """

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 150,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    logger.error(
                        "OpenAI API error",
                        extra={
                            "status_code": response.status_code,
                            "error": error_msg,
                            "response": error_data,
                        },
                    )
                    raise Exception(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                content = _validate_openai_response(data)

                # Parse JSON response
                try:
                    parsed = _safe_json_loads(content)
                    confidence = 0.8  # Default confidence for AI responses

                    return {
                        "category": parsed["category"],
                        "confidence": confidence,
                        "rationale": parsed["rationale"],
                        "meta": {
                            "model": settings.model_name,
                            "cost": self._estimate_cost(data.get("usage", {})),
                            "fallback": False,
                        },
                    }
                except Exception as json_error:
                    logger.warning(
                        "Failed to parse OpenAI JSON response",
                        extra={"raw_content": content, "error": str(json_error)},
                    )
                    return {
                        "category": "Produtivo",
                        "confidence": 0.5,
                        "rationale": "Erro na resposta da IA",
                        "meta": {
                            "model": settings.model_name,
                            "cost": 0.0,
                            "fallback": True,
                        },
                    }

        except Exception:
            logger.error("OpenAI classification error", exc_info=True)
            raise

    async def _generate_reply_openai(self, text: str, category: str, tone: str) -> str:
        """Generate reply using OpenAI"""
        # Validate API key is configured
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        tone_map = {
            "formal": "formal",
            "neutro": "neutro",
            "amigavel": "amigável",
        }

        prompt = f"""Contexto: Você é um assistente de atendimento educado e objetivo.
Categoria: {category}
Tom: {tone_map.get(tone, tone)}

Regras:
- 3 a 6 linhas, claras.
- Se "Produtivo": reconhecer pedido, apontar próximo passo, solicitar dados
faltantes (ex: nº do chamado/protocolo), dar prazo estimado.
- Se "Improdutivo": agradecer e encerrar com cordialidade.
- Não inclua disclaimers sobre IA; apenas o corpo do e-mail.

E-mail recebido:
\"\"\"{text}\"\"\""""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 300,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    logger.error(
                        "OpenAI API error during reply generation",
                        extra={
                            "status_code": response.status_code,
                            "error": error_msg,
                            "response": error_data,
                        },
                    )
                    raise Exception(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                content = _validate_openai_response(data)
                return content

        except Exception:
            logger.error("OpenAI reply generation error", exc_info=True)
            raise

    async def _refine_reply_openai(self, reply: str, tone: str) -> str:
        """Refine reply using OpenAI"""
        # Validate API key is configured
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Tarefa: Reescrever mantendo o mesmo sentido, ajustando o tom para {tone} e deixando mais conciso.
Texto atual:
\"\"\"{reply}\"\"\"
Responda apenas com o corpo revisado."""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 300,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    logger.error(
                        "OpenAI API error during refinement",
                        extra={
                            "status_code": response.status_code,
                            "error": error_msg,
                            "response": error_data,
                        },
                    )
                    raise Exception(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                content = _validate_openai_response(data)
                return content

        except Exception:
            logger.error("OpenAI reply refinement error", exc_info=True)
            raise

    async def _classify_huggingface(self, text: str) -> Dict[str, Any]:
        """HuggingFace classification - placeholder implementation"""
        # This would implement HF API calls
        # For now, fallback to heuristics
        category, confidence, rationale = classify_heuristic(text)
        return {
            "category": category,
            "confidence": confidence,
            "rationale": rationale,
            "meta": {
                "model": "heuristic_fallback",
                "cost": 0.0,
                "fallback": True,
            },
        }

    async def _generate_reply_huggingface(
        self, text: str, category: str, tone: str
    ) -> str:
        """Generate reply using HuggingFace"""
        return self._generate_reply_fallback(category, tone)

    async def _refine_reply_huggingface(self, reply: str, tone: str) -> str:
        """Refine reply using HuggingFace"""
        return reply

    def _generate_reply_fallback(self, category: str, tone: str) -> str:
        """Fallback reply generation"""
        if category == "Produtivo":
            if tone == "formal":
                return (
                    "Prezado(a),\n\nRecebemos sua solicitação e ela será analisada pela "
                    "nossa equipe. Para melhor atendimento, favor informar o número do "
                    "protocolo caso já possua. Retornaremos em até 24 horas úteis.\n\n"
                    "Atenciosamente,\nEquipe de Suporte"
                )
            elif tone == "amigavel":
                return (
                    "Olá! 😊\n\nObrigado por entrar em contato! Sua mensagem já chegou "
                    "aqui e vamos analisar com cuidado. Se tiver algum número de "
                    "protocolo, pode compartilhar que vai acelerar o processo. Voltamos "
                    "a falar em breve!\n\nUm abraço,\nTime de Suporte"
                )
            else:
                return (
                    "Olá,\n\nSua solicitação foi recebida e será analisada. "
                    "Caso tenha número de protocolo, informe para agilizar o atendimento. "
                    "Prazo de resposta: até 24h úteis.\n\nSaúde,\nSuporte"
                )
        else:
            if tone == "formal":
                return (
                    "Prezado(a),\n\nAgradecemos pelo contato e pela confiança em nossos serviços. "
                    "Sua mensagem foi muito importante para nós.\n\nAtenciosamente,\nEquipe"
                )
            elif tone == "amigavel":
                return (
                    "Oi! 😊\n\nQue legal receber sua mensagem! Obrigado pelas palavras, "
                    "ficamos muito felizes. Continue sempre em contato!\n\nUm abraço,\nTime"
                )
            else:
                return (
                    "Olá,\n\nObrigado pelo contato. Sua mensagem foi recebida "
                    "e muito apreciada.\n\nSaudações,\nEquipe"
                )

    def _estimate_cost(self, usage: Dict) -> float:
        """Estimate API call cost"""
        if not usage:
            return 0.0

        # Rough estimation for GPT-4o-mini (example rates)
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # Example rates per 1K tokens
        input_rate = 0.00015  # $0.15 per 1K tokens
        output_rate = 0.0006  # $0.60 per 1K tokens

        cost = (input_tokens * input_rate / 1000) + (output_tokens * output_rate / 1000)
        return round(cost, 6)

    def _calculate_confidence(self, text: str, result: dict) -> float:
        """
        Calculate confidence score based on text and classification
        """
        confidence_factors = {
            "clear_keywords": 0.3,
            "text_length": 0.2,
            "rationale_quality": 0.3,
            "category_certainty": 0.2,
        }

        score = 0.0

        # Check for clear keywords
        produtivo_keywords = [
            "problema",
            "erro",
            "ajuda",
            "suporte",
            "acesso",
            "protocolo",
            "chamado",
        ]
        improdutivo_keywords = [
            "obrigado",
            "parabéns",
            "feliz",
            "agradecimento",
        ]

        text_lower = text.lower()
        if any(kw in text_lower for kw in produtivo_keywords):
            score += confidence_factors["clear_keywords"]
        elif any(kw in text_lower for kw in improdutivo_keywords):
            score += confidence_factors["clear_keywords"]

        # Text length factor (medium length texts are more reliable)
        word_count = len(text.split())
        if 10 <= word_count <= 100:
            score += confidence_factors["text_length"]

        # Rationale quality (length as proxy)
        rationale = result.get("rationale", "")
        if len(rationale) > 20:
            score += confidence_factors["rationale_quality"]

        # Always add base category certainty
        score += confidence_factors["category_certainty"]

        return min(1.0, score)

    async def _classify_openai_with_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        OpenAI classification with custom prompt
        """
        # Validate API key is configured
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 150,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    logger.error(
                        "OpenAI API error",
                        extra={
                            "status_code": response.status_code,
                            "error": error_msg,
                            "response": error_data,
                        },
                    )
                    raise Exception(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                content = _validate_openai_response(data)

                try:
                    result = _safe_json_loads(content)
                    result["meta"] = {
                        "model": settings.model_name,
                        "cost": self._estimate_cost(data.get("usage", {})),
                        "fallback": False,
                    }
                    return result
                except Exception as json_error:
                    logger.warning(
                        "Failed to parse OpenAI JSON response",
                        extra={"raw_content": content, "error": str(json_error)},
                    )
                    return {
                        "category": "Produtivo",
                        "rationale": "Erro na resposta da IA",
                        "meta": {
                            "model": settings.model_name,
                            "fallback": True,
                        },
                    }

        except Exception:
            logger.error("OpenAI classification error", exc_info=True)
            raise

    async def _generate_reply_openai_with_prompt(self, prompt: str) -> str:
        """
        Generate reply using OpenAI with custom prompt
        """
        # Validate API key is configured
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 300,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    logger.error(
                        "OpenAI API error",
                        extra={
                            "status_code": response.status_code,
                            "error": error_msg,
                            "response": error_data,
                        },
                    )
                    raise Exception(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                content = _validate_openai_response(data)
                return content

        except Exception:
            logger.error("OpenAI reply generation error", exc_info=True)
            raise


# Global AI provider instance
ai_provider = AIProvider()
