"""Vector retrieval engine enforcing database-level RBAC filtering and relevance thresholding."""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import RetrievalError
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.user import UserRole
from app.api.dependencies import get_authorized_roles
from app.embeddings.service import embedding_service


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_title: str
    chunk_text: str
    page_number: Optional[int]
    section_heading: Optional[str]
    similarity_score: float
    audience_role: UserRole


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two float vectors: (A . B) / (||A|| * ||B||)."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def search_vector_store(
    db: Session,
    query_text: str,
    user_role: UserRole,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None,
) -> List[RetrievedChunk]:
    """Retrieve relevant chunks strictly enforcing DB-level RBAC and similarity thresholds.

    CRITICAL SECURITY REQUIREMENT:
    Document access restrictions are applied directly within the database query
    filter before content ever enters application context or LLM prompt.
    """
    k = top_k or settings.TOP_K_CHUNKS
    threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

    # 1. Generate query embedding
    query_vector = embedding_service.embed_query(query_text)
    if not embedding_service.validate_dimension(query_vector):
        raise RetrievalError(f"Query vector dimension invalid (expected {settings.EMBEDDING_DIMENSION})")

    # 2. Determine authorized audience roles based on server-verified user_role
    authorized_roles = get_authorized_roles(user_role)

    # 3. Check database dialect
    dialect_name = db.bind.dialect.name if db.bind else "sqlite"

    retrieved: List[RetrievedChunk] = []

    if dialect_name == "postgresql":
        # Native pgvector cosine similarity search:
        # Distance operator `<=>` computes cosine distance (0 = identical, 2 = opposite).
        # Cosine similarity = 1 - cosine_distance.
        # Max cosine distance corresponding to threshold = 1 - threshold.
        max_distance = 1.0 - threshold

        sql_query = text("""
            SELECT 
                c.id AS chunk_id,
                c.document_id AS document_id,
                d.title AS document_title,
                c.chunk_text AS chunk_text,
                c.page_number AS page_number,
                c.section_heading AS section_heading,
                c.audience_role AS audience_role,
                (1 - (c.embedding <=> :query_vector::vector)) AS similarity
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.audience_role = ANY(:roles)
              AND d.processing_status = 'completed'
              AND (c.embedding <=> :query_vector::vector) <= :max_distance
            ORDER BY c.embedding <=> :query_vector::vector ASC
            LIMIT :top_k;
        """)

        try:
            results = db.execute(
                sql_query,
                {
                    "query_vector": str(query_vector),
                    "roles": [r.value for r in authorized_roles],
                    "max_distance": max_distance,
                    "top_k": k,
                },
            ).fetchall()

            for row in results:
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=row.chunk_id,
                        document_id=row.document_id,
                        document_title=row.document_title,
                        chunk_text=row.chunk_text,
                        page_number=row.page_number,
                        section_heading=row.section_heading,
                        similarity_score=round(float(row.similarity), 4),
                        audience_role=UserRole(row.audience_role),
                    )
                )
        except Exception as exc:
            logger.error("PostgreSQL pgvector search failed: %s. Falling back to ORM retrieval.", exc)
            dialect_name = "fallback"

    if dialect_name != "postgresql" or not retrieved:
        # Dual-dialect fallback (e.g. SQLite testing or fallback):
        # 1. Fetch chunks matching audience_role inside DB
        query = (
            db.query(DocumentChunk, Document.title)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(
                DocumentChunk.audience_role.in_(authorized_roles),
            )
        )
        candidates = query.all()

        scored_candidates = []
        for chunk_obj, doc_title in candidates:
            if chunk_obj.embedding is None:
                continue
            chunk_vec = chunk_obj.embedding
            if isinstance(chunk_vec, str):
                import json
                try:
                    chunk_vec = json.loads(chunk_vec)
                except Exception:
                    continue

            sim = compute_cosine_similarity(query_vector, chunk_vec)
            # Apply threshold filtering
            if sim >= threshold:
                scored_candidates.append((sim, chunk_obj, doc_title))

        # Sort descending by similarity
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        for sim, chunk_obj, doc_title in scored_candidates[:k]:
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_obj.id,
                    document_id=chunk_obj.document_id,
                    document_title=doc_title,
                    chunk_text=chunk_obj.chunk_text,
                    page_number=chunk_obj.page_number,
                    section_heading=chunk_obj.section_heading,
                    similarity_score=round(float(sim), 4),
                    audience_role=chunk_obj.audience_role,
                )
            )

    logger.info(
        "Retrieved %d authorized chunks for query '%s' [Role=%s, MinThreshold=%.2f]",
        len(retrieved),
        query_text[:50],
        user_role.value,
        threshold,
    )
    return retrieved
