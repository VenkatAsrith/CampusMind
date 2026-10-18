"""Document ingestion service coordinating upload, extraction, chunking, and vector storage."""

import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import IngestionError
from app.models.document import Document, ProcessingStatus
from app.models.chunk import DocumentChunk
from app.models.user import UserRole
from app.ingestion.validator import validate_uploaded_file
from app.ingestion.extractor import extract_document_text
from app.ingestion.chunker import chunk_document_sections
from app.embeddings.service import embedding_service


def ingest_document(
    db: Session,
    filename: str,
    content: bytes,
    uploader_id: int,
    audience_role: UserRole = UserRole.STUDENT,
    custom_title: Optional[str] = None,
) -> Document:
    """Execute complete ingestion pipeline for a single document.

    Steps:
    1. Validation & sanitization (size, extension, SHA-256)
    2. Duplicate check (warn or update)
    3. Creation of Document in PROCESSING status
    4. Text extraction (PDF/DOCX/TXT)
    5. Cleaning & Semantic Chunking
    6. Batch Vector Embedding generation
    7. Persistence of DocumentChunks with denormalized audience_role
    8. Status update to COMPLETED
    """
    clean_filename, ext, content_hash, file_size = validate_uploaded_file(filename, content)
    doc_title = custom_title or os.path.splitext(clean_filename)[0].replace("_", " ").title()

    # Create initial Document record in DB
    document = Document(
        filename=clean_filename,
        title=doc_title,
        document_type=ext,
        file_size_bytes=file_size,
        content_hash=content_hash,
        uploader_id=uploader_id,
        audience_role=audience_role,
        processing_status=ProcessingStatus.PROCESSING,
        chunk_count=0,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        # Step 4: Extract text sections
        sections = extract_document_text(ext, content)

        # Step 5: Semantic Chunking
        chunk_dicts = chunk_document_sections(sections)
        if not chunk_dicts:
            raise IngestionError("Document yielded zero usable text chunks after extraction")

        # Step 6: Generate Embeddings in batch
        chunk_texts = [c["chunk_text"] for c in chunk_dicts]
        embeddings = embedding_service.embed_batch(chunk_texts)

        # Step 7: Persist DocumentChunks
        db_chunks = []
        for i, c in enumerate(chunk_dicts):
            chunk_obj = DocumentChunk(
                document_id=document.id,
                chunk_index=c["chunk_index"],
                chunk_text=c["chunk_text"],
                page_number=c.get("page_number"),
                section_heading=c.get("section_heading"),
                audience_role=audience_role,
                embedding=embeddings[i],
            )
            db_chunks.append(chunk_obj)

        db.add_all(db_chunks)

        # Step 8: Update document status
        document.processing_status = ProcessingStatus.COMPLETED
        document.chunk_count = len(db_chunks)
        document.error_message = None
        document.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(document)

        logger.info(
            "Document '%s' (ID=%d) successfully ingested with %d chunks (audience=%s)",
            document.title,
            document.id,
            document.chunk_count,
            document.audience_role.value,
        )
        return document

    except Exception as exc:
        db.rollback()
        logger.error("Document ingestion failed for '%s': %s", filename, exc)
        document.processing_status = ProcessingStatus.FAILED
        document.error_message = str(exc)
        document.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(document)
        raise IngestionError(f"Ingestion failed: {str(exc)}")
