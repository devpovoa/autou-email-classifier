import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai import ai_provider
from app.services.nlp import preprocess_text
from app.utils.pdf import extract_text_from_pdf, validate_pdf
from app.utils.txt import extract_text_from_txt, validate_txt

logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/web/templates")
router = APIRouter()


class ClassifyRequest(BaseModel):
    text: str
    tone: str = "neutro"


class RefineRequest(BaseModel):
    text: str
    tone: str


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.post("/classify")
async def classify_email(
    request: Request,
    text: Optional[str] = Form(None),
    tone: str = Form("neutro"),
    file: Optional[UploadFile] = File(None)
):
    """Classify email and generate response"""
    start_time = time.time()

    try:
        # Extract text from file or form
        email_text = await _extract_text(text, file)

        # Validate input
        if not email_text or len(email_text.strip()) < 5:
            raise HTTPException(
                status_code=400, detail="Texto muito curto ou vazio")

        if len(email_text) > settings.max_input_chars:
            raise HTTPException(
                status_code=400,
                detail=f"Texto excede o limite de {settings.max_input_chars} caracteres"
            )

        # Preprocess text
        processed_text = preprocess_text(email_text)

        # Classify using AI
        classification = await ai_provider.classify(processed_text)

        # Generate reply
        reply = await ai_provider.generate_reply(
            processed_text,
            classification["category"],
            tone
        )

        # Calculate response time
        latency_ms = max(1, round((time.time() - start_time) * 1000))

        # Log the operation
        logger.info("Classification completed successfully",
                    text_length=len(email_text),
                    category=classification["category"],
                    confidence=classification["confidence"],
                    tone=tone,
                    latency_ms=latency_ms,
                    model=classification["meta"]["model"],
                    fallback=classification["meta"].get("fallback", False))

        # Return response
        response = {
            "category": classification["category"],
            "confidence": classification["confidence"],
            "reply": reply,
            "rationale": classification["rationale"],
            "meta": classification["meta"],
            "latency_ms": latency_ms
        }

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = max(1, round((time.time() - start_time) * 1000))
        logger.error("Classification failed",
                     error=str(e),
                     latency_ms=latency_ms)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/refine")
async def refine_reply(request: RefineRequest):
    """Refine existing reply with new tone"""
    start_time = time.time()

    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400, detail="Texto muito curto para refinar")

        # Refine the reply
        refined_reply = await ai_provider.refine_reply(request.text, request.tone)

        latency_ms = round((time.time() - start_time) * 1000)

        logger.info("Reply refined successfully",
                    original_length=len(request.text),
                    refined_length=len(refined_reply),
                    tone=request.tone,
                    latency_ms=latency_ms)

        return JSONResponse(content={
            "reply": refined_reply,
            "latency_ms": latency_ms
        })

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000)
        logger.error("Reply refinement failed",
                     error=str(e),
                     latency_ms=latency_ms)
        raise HTTPException(status_code=500, detail="Erro ao refinar resposta")


async def _extract_text(form_text: Optional[str], file: Optional[UploadFile]) -> str:
    """Extract text from form input or uploaded file"""

    if form_text and form_text.strip():
        return form_text.strip()

    if file and file.filename:
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande (máximo: {settings.max_file_size // 1024 // 1024}MB)"
            )

        # Process based on file extension
        filename_lower = file.filename.lower()

        if filename_lower.endswith('.pdf'):
            if not validate_pdf(file_content):
                raise HTTPException(
                    status_code=400, detail="Arquivo PDF inválido")

            text = extract_text_from_pdf(file_content)
            if not text:
                raise HTTPException(
                    status_code=400, detail="Não foi possível extrair texto do PDF")
            return text

        elif filename_lower.endswith(('.txt', '.text')):
            if not validate_txt(file_content):
                raise HTTPException(
                    status_code=400, detail="Arquivo TXT inválido")

            text = extract_text_from_txt(file_content)
            if not text:
                raise HTTPException(
                    status_code=400, detail="Não foi possível extrair texto do arquivo")
            return text

        else:
            raise HTTPException(
                status_code=400, detail="Tipo de arquivo não suportado (apenas .txt e .pdf)")

    raise HTTPException(
        status_code=400, detail="Nenhum texto ou arquivo fornecido")
