"""Application configuration module using Pydantic Settings."""

from typing import List, Union, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "CampusMind Backend"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & JWT
    JWT_SECRET_KEY: str = "default_development_secret_key_campusmind_rag_2026_super_secure_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database
    DATABASE_URL: str = "sqlite:///./campusmind_dev.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"
    USE_MOCK_EMBEDDINGS: bool = False

    # Retrieval & RAG
    TOP_K_CHUNKS: int = 4
    SIMILARITY_THRESHOLD: float = 0.30
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    # Ingestion & Uploads
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_EXTENSIONS: str = "pdf,docx,txt"
    UPLOAD_DIR: str = "./data/uploads"

    # LLM Settings
    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_API_KEY: str = "mock-key-for-campusmind"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 800
    LLM_REQUEST_TIMEOUT_SECONDS: float = 30.0
    LLM_MAX_RETRIES: int = 2
    USE_MOCK_LLM: bool = False

    # CORS
    CORS_ORIGINS: Optional[Union[str, List[str]]] = None
    ALLOWED_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins(self) -> List[str]:
        raw_val = self.CORS_ORIGINS if self.CORS_ORIGINS is not None else self.ALLOWED_CORS_ORIGINS
        if isinstance(raw_val, list):
            raw_list = raw_val
        else:
            raw_list = [origin.strip() for origin in str(raw_val).split(",") if origin.strip()]

        normalized: List[str] = []
        for o in raw_list:
            cleaned = o.strip().rstrip("/")
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized if normalized else ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def allowed_extensions(self) -> List[str]:
        return [ext.strip().lower().lstrip(".") for ext in self.ALLOWED_FILE_EXTENSIONS.split(",") if ext.strip()]


# Global settings singleton
settings = Settings()
