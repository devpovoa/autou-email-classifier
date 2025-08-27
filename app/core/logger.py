import json
import logging
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


def setup_logging():
    """Configure structured JSON logging"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s",
        handlers=[logging.StreamHandler()]
    )


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def _log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(getattr(logging, level),
                        json.dumps(log_entry, default=str))


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)
