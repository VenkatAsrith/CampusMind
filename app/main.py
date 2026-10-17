"""FastAPI main application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import CampusMindException
from app.db.base import Base
from app.db.session import engine
import app.models  # Ensure all ORM models are registered with Base.metadata
from app.api.routes import (
    auth_router,
    chat_router,
    conversations_router,
    documents_router,
    health_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown procedures."""
    logger.info("Initializing %s in [%s] mode...", settings.APP_NAME, settings.ENVIRONMENT)
    try:
        # Create database tables if they do not exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified and initialized.")
    except Exception as exc:
        logger.error("Database schema initialization warning: %s", exc)

    yield

    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="CampusMind: AI-Powered Campus Information Assistant API with pgvector and RBAC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(CampusMindException)
async def campusmind_exception_handler(request: Request, exc: CampusMindException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if exc.error_code in ("AUTHENTICATION_FAILED", "INACTIVE_USER"):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif exc.error_code == "PERMISSION_DENIED":
        status_code = status.HTTP_403_FORBIDDEN
    elif exc.error_code == "NOT_FOUND":
        status_code = status.HTTP_404_NOT_FOUND
    elif exc.error_code in ("VALIDATION_ERROR", "INGESTION_ERROR"):
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact the administrator.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# Attach API Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(conversations_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
