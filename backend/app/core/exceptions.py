"""Application exceptions and error schemas."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class CampusMindException(Exception):
    """Base exception for all CampusMind application errors."""

    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(CampusMindException):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message, error_code="AUTHENTICATION_FAILED")


class AuthorizationError(CampusMindException):
    """Raised when an authenticated user lacks required permissions."""

    def __init__(self, message: str = "Operation not permitted"):
        super().__init__(message, error_code="PERMISSION_DENIED")


class InactiveUserError(CampusMindException):
    """Raised when an inactive user attempts an authenticated action."""

    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message, error_code="INACTIVE_USER")


class ResourceNotFoundError(CampusMindException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(f"{resource} with identifier '{identifier}' not found", error_code="NOT_FOUND")


class ValidationError(CampusMindException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


class IngestionError(CampusMindException):
    """Raised when document ingestion, extraction, or chunking fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="INGESTION_ERROR", details=details)


class RetrievalError(CampusMindException):
    """Raised when vector retrieval encounters database or dimension failures."""

    def __init__(self, message: str):
        super().__init__(message, error_code="RETRIEVAL_ERROR")


class LLMServiceError(CampusMindException):
    """Raised when LLM provider encounters network, timeout, or rate-limit failures."""

    def __init__(self, message: str):
        super().__init__(message, error_code="LLM_SERVICE_ERROR")


class InsufficientEvidenceError(CampusMindException):
    """Raised when vector retrieval finds no authorized chunks meeting relevance threshold."""

    def __init__(self, message: str = "Insufficient evidence in authorized campus documents to answer this question."):
        super().__init__(message, error_code="INSUFFICIENT_EVIDENCE")
