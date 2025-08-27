from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI Provider Settings
    provider: str = "OpenAI"  # OpenAI or HF
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    hf_token: Optional[str] = None
    model_name: str = "gpt-4o-mini"

    # App Settings
    app_env: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    max_input_chars: int = 5000
    max_file_size: int = 2 * 1024 * 1024  # 2MB

    # JWT Security Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours
    jwt_refresh_token_expire_days: int = 7  # 7 days
    
    # API Security
    enable_auth: bool = True
    api_key_header: str = "X-API-Key"
    default_api_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour

    # AI Configuration
    use_heuristic_fallback: bool = True
    confidence_threshold: float = 0.7
    heuristic_keywords_urgent: str = "urgente,emergencia,asap,critico,imediato"
    heuristic_keywords_thanks: str = (
        "obrigado,agradeco,thanks,grateful,appreciate"
    )
    heuristic_keywords_normal: str = (
        "informacao,consulta,duvida,question,inquiry"
    )

    # Development specific
    reload: bool = False
    workers: int = 1

    # Timeouts
    ai_timeout: int = 30

    model_config = {"protected_namespaces": (), "env_file": ".env"}


settings = Settings()
