"""Document Chunk database model with vector embedding support."""

import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import UserRole
from app.core.config import settings

try:
    from pgvector.sqlalchemy import Vector as PGVector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    PGVector = None


class VectorType(TypeDecorator):
    """Custom SQLAlchemy type that uses pgvector Vector on PostgreSQL,
    and a JSON-serialized TEXT column on SQLite/non-PostgreSQL environments.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dimension: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimension = dimension

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR and PGVector is not None:
            return dialect.type_descriptor(PGVector(self.dimension))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return list(value) if hasattr(value, "__iter__") else value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Denormalized for direct vector query indexing and role filtering
    audience_role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="chunk_audience_role_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=UserRole.STUDENT,
        index=True,
    )

    # Vector embedding column (dimension configured from settings, default 384)
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        VectorType(dimension=settings.EMBEDDING_DIMENSION),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, idx={self.chunk_index}, role='{self.audience_role}')>"
