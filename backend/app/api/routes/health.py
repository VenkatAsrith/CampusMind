"""Health and readiness check endpoints for monitoring and container orchestration."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import HealthResponse, ReadinessResponse
from app.embeddings.service import embedding_service

router = APIRouter(tags=["Health & Monitoring"])


@router.get("/health", response_model=HealthResponse)
def liveness_check():
    """Liveness probe indicating that the FastAPI process is responsive."""
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        version="1.0.0",
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe verifying database connectivity, vector support, and embedding service."""
    db_status = "connected"
    vector_support = False

    try:
        db.execute(text("SELECT 1")).scalar()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    try:
        # Check pgvector extension on PostgreSQL
        if db.bind and db.bind.dialect.name == "postgresql":
            val = db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
            vector_support = bool(val)
        else:
            # Dual-dialect mode active for SQLite/fallback
            vector_support = True
    except Exception:
        vector_support = False

    return ReadinessResponse(
        status="ready" if db_status == "connected" else "not_ready",
        database=db_status,
        vector_support=vector_support,
        embedding_dimension=embedding_service.dimension,
    )
