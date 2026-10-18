"""Common API response and error schemas."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error explanation")
    error_code: str = Field("INTERNAL_ERROR", description="Standardized error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional diagnostic details")


class HealthResponse(BaseModel):
    status: str = Field("ok", json_schema_extra={"example": "ok"})
    app_name: str
    environment: str
    version: str = "1.0.0"


class ReadinessResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ready"})
    database: str = Field(..., json_schema_extra={"example": "connected"})
    vector_support: bool = Field(..., json_schema_extra={"example": True})
    embedding_dimension: int = Field(..., json_schema_extra={"example": 384})
