"""Application logging configuration with structured sanitization."""

import logging
import re
import sys
from typing import Any, Dict
from app.core.config import settings

# Patterns for sensitive values that must never appear in log files
SENSITIVE_PATTERNS = [
    (re.compile(r'(password[\'"]?\s*[:=]\s*[\'"]?)([^\'",\s]+)', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(bearer\s+)([a-zA-Z0-9_\-\.]+)', re.IGNORECASE), r'\1[REDACTED_TOKEN]'),
    (re.compile(r'(api_key[\'"]?\s*[:=]\s*[\'"]?)([^\'",\s]+)', re.IGNORECASE), r'\1[REDACTED_KEY]'),
    (re.compile(r'(secret[\'"]?\s*[:=]\s*[\'"]?)([^\'",\s]+)', re.IGNORECASE), r'\1[REDACTED_SECRET]'),
]


class SanitizedFormatter(logging.Formatter):
    """Custom logging formatter that scrubs passwords, bearer tokens, and secrets."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        sanitized = original
        for pattern, replacement in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if called multiple times
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = SanitizedFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    app_logger = logging.getLogger("campusmind")
    app_logger.setLevel(log_level)
    return app_logger


logger = setup_logging()
