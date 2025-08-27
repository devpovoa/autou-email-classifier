import os
import sys

from fastapi import FastAPI

from app.core.logger import setup_logging
from app.web.routes import router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> FastAPI:
    app = FastAPI(
        title="AutoU - Classificador de E-mails",
        description="Sistema inteligente de classificação e resposta automática de e-mails",
        version="1.0.0",
    )

    # Setup logging
    setup_logging()

    # Include routes
    app.include_router(router)

    return app


app = create_app()
