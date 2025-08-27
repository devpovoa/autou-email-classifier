import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.core.auth import (
    Token,
    User,
    api_key_auth,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    rate_limit_check,
    require_scopes,
)
from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai import ai_provider
from app.services.nlp import preprocess_text
from app.utils.pdf import extract_text_from_pdf, validate_pdf
from app.utils.txt import extract_text_from_txt, validate_txt

logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/web/templates")
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class ClassifyRequest(BaseModel):
    text: str
    tone: str = "neutro"


class RefineRequest(BaseModel):
    text: str
    tone: str


class ClassificationMeta(BaseModel):
    model: str
    cost: float = 0.0
    fallback: bool = False


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    rationale: str
    meta: ClassificationMeta
    latency_ms: int


class ClassifyResponse(ClassificationResponse):
    reply: str


class RefineResponse(BaseModel):
    reply: str
    latency_ms: int


class APIClassificationResponse(BaseModel):
    category: str
    confidence: float
    rationale: str
    meta: ClassificationMeta
    user: str
    timestamp: str
    filename: Optional[str] = None


class LegacyClassificationResponse(BaseModel):
    category: str
    confidence: float
    rationale: str
    meta: ClassificationMeta
    auth_method: str
    timestamp: str


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Authentication endpoints
@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint.

    Get access token for interactive API docs.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user scopes
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user.username, "scopes": user.scopes}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
    }


@router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


# Protected classification endpoints
@router.post("/api/classify/text", response_model=APIClassificationResponse)
async def classify_text_api(
    request: ClassifyRequest,
    current_user: User = Depends(require_scopes("classify:read")),
    _: bool = Depends(rate_limit_check),
):
    """
    Classify email text via API (JWT protected).

    Requires 'classify:read' scope.
    """
    try:
        if len(request.text) > settings.max_input_chars:
            raise HTTPException(
                status_code=400,
                detail=f"Text exceeds limit of {settings.max_input_chars}",
            )

        # Preprocess text
        processed_text = preprocess_text(request.text)

        # Classify with AI
        result = await ai_provider.classify(processed_text)

        # Add user context
        result["user"] = current_user.username
        result["timestamp"] = datetime.utcnow().isoformat()

        return result

    except Exception as e:
        logger.error(
            "Classification error for authenticated user",
            extra={
                "user": current_user.username,
                "error": str(e),
                "text_length": len(request.text),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro na classificação")


@router.post("/api/classify/file", response_model=APIClassificationResponse)
async def classify_file_api(
    file: UploadFile = File(...),
    current_user: User = Depends(require_scopes("classify:read")),
    _: bool = Depends(rate_limit_check),
):
    """
    Classify email file via API (JWT protected).

    Requires 'classify:read' scope.
    Supports PDF and TXT files.
    """
    try:
        # Extract text from file
        text = await _extract_text(None, file)

        # Preprocess text
        processed_text = preprocess_text(text)

        # Classify with AI
        result = await ai_provider.classify(processed_text)

        # Add metadata
        result["user"] = current_user.username
        result["filename"] = file.filename
        result["timestamp"] = datetime.utcnow().isoformat()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "File classification error for authenticated user",
            extra={
                "user": current_user.username,
                "filename": file.filename,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro na classificação do arquivo")


# Alternative API key authentication (for legacy systems)
@router.post("/api/v1/classify", response_model=LegacyClassificationResponse)
async def classify_with_api_key(
    request: ClassifyRequest, api_key: str = Depends(api_key_auth)
):
    """
    Classify email text using API key authentication.

    Legacy endpoint for systems that cannot use JWT.
    """
    try:
        if len(request.text) > settings.max_input_chars:
            raise HTTPException(
                status_code=400,
                detail=f"Text exceeds limit of {settings.max_input_chars}",
            )

        # Preprocess text
        processed_text = preprocess_text(request.text)

        # Classify with AI
        result = await ai_provider.classify(processed_text)

        # Add metadata
        result["auth_method"] = "api_key"
        result["timestamp"] = datetime.utcnow().isoformat()

        return result

    except Exception as e:
        logger.error(
            "API key classification error",
            extra={"error": str(e), "text_length": len(request.text)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro na classificação")


@router.post("/classify", response_model=ClassifyResponse)
async def classify_email(
    request: Request,
    text: Optional[str] = Form(None),
    tone: str = Form("neutro"),
    file: Optional[UploadFile] = File(None),
):
    """Classify email and generate response"""
    start_time = time.time()

    try:
        # Extract text from file or form
        email_text = await _extract_text(text, file)

        # Validate input
        if not email_text or len(email_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Texto muito curto ou vazio")

        if len(email_text) > settings.max_input_chars:
            raise HTTPException(
                status_code=400,
                detail=f"Texto excede o limite de {settings.max_input_chars} caracteres",
            )

        # Preprocess text
        processed_text = preprocess_text(email_text)

        # Classify using AI
        classification = await ai_provider.classify(processed_text)

        # Generate reply
        reply = await ai_provider.generate_reply(
            processed_text, classification["category"], tone
        )

        # Calculate response time
        latency_ms = max(1, round((time.time() - start_time) * 1000))

        # Log the operation
        logger.info(
            "Classification completed successfully",
            text_length=len(email_text),
            category=classification["category"],
            confidence=classification["confidence"],
            tone=tone,
            latency_ms=latency_ms,
            model=classification["meta"]["model"],
            fallback=classification["meta"].get("fallback", False),
        )

        # Return response
        response = {
            "category": classification["category"],
            "confidence": classification["confidence"],
            "reply": reply,
            "rationale": classification["rationale"],
            "meta": classification["meta"],
            "latency_ms": latency_ms,
        }

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = max(1, round((time.time() - start_time) * 1000))
        logger.error(
            "Classification failed",
            extra={
                "error": str(e),
                "latency_ms": latency_ms,
                "text_length": len(email_text) if "email_text" in locals() else 0,
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/refine", response_model=RefineResponse)
async def refine_reply(request: RefineRequest):
    """Refine existing reply with new tone"""
    start_time = time.time()

    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400, detail="Texto muito curto para refinar"
            )

        # Refine the reply
        refined_reply = await ai_provider.refine_reply(request.text, request.tone)

        latency_ms = round((time.time() - start_time) * 1000)

        logger.info(
            "Reply refined successfully",
            original_length=len(request.text),
            refined_length=len(refined_reply),
            tone=request.tone,
            latency_ms=latency_ms,
        )

        return JSONResponse(content={"reply": refined_reply, "latency_ms": latency_ms})

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000)
        logger.error(
            "Reply refinement failed",
            extra={
                "error": str(e),
                "latency_ms": latency_ms,
                "original_length": len(request.text),
                "tone": request.tone,
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro ao refinar resposta")


async def _extract_text(form_text: Optional[str], file: Optional[UploadFile]) -> str:
    """Extract text from form input or uploaded file"""

    if form_text and form_text.strip():
        return form_text.strip()

    if file and file.filename:
        # Read file content once
        file_content = await file.read()

        # Check file size before processing
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande (máximo: {settings.max_file_size // 1024 // 1024}MB)",
            )

        # Process based on file extension
        filename_lower = file.filename.lower()

        if filename_lower.endswith(".pdf"):
            if not validate_pdf(file_content):
                raise HTTPException(
                    status_code=400, detail="Arquivo PDF inválido ou corrompido"
                )

            text = extract_text_from_pdf(file_content)
            if not text or len(text.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não foi possível extrair texto do PDF",
                )
            return text.strip()

        elif filename_lower.endswith((".txt", ".text")):
            if not validate_txt(file_content):
                raise HTTPException(
                    status_code=400, detail="Arquivo TXT inválido ou corrompido"
                )

            text = extract_text_from_txt(file_content)
            if not text or len(text.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não foi possível extrair texto do arquivo",
                )
            return text.strip()

        else:
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo não suportado. Use apenas .txt ou .pdf",
            )

    raise HTTPException(
        status_code=400,
        detail="É necessário fornecer texto ou fazer upload de um arquivo",
    )
