"""Admin document management endpoints (Upload, List, Detail, Delete)."""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import Document, ProcessingStatus
from app.schemas.document import DocumentListResponse, DocumentRead, DocumentUploadResponse, AdminStatsResponse
from app.api.dependencies import require_admin
from app.ingestion.service import ingest_document

router = APIRouter(prefix="/admin/documents", tags=["Admin Document Management"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .docx, .txt)"),
    audience_role: UserRole = Form(UserRole.STUDENT, description="Target clearance role (student, faculty, admin)"),
    title: Optional[str] = Form(None, description="Optional custom title for the document"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Upload and ingest a campus knowledge document. Enforces Administrator role."""
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        doc = ingest_document(
            db=db,
            filename=file.filename or "upload.txt",
            content=content,
            uploader_id=admin_user.id,
            audience_role=audience_role,
            custom_title=title,
        )
        return DocumentUploadResponse(
            message=f"Document '{doc.title}' uploaded and processed successfully",
            document=DocumentRead.model_validate(doc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing failed: {str(exc)}",
        )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all ingested documents and their status. Enforces Administrator role."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(
        total=len(docs),
        documents=[DocumentRead.model_validate(d) for d in docs],
    )


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_document_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve operational knowledge-base statistics for Administrator dashboard."""
    docs = db.query(Document).all()
    total_docs = len(docs)
    completed_docs = sum(1 for d in docs if d.processing_status == ProcessingStatus.COMPLETED)
    pending_docs = sum(1 for d in docs if d.processing_status in (ProcessingStatus.PENDING, ProcessingStatus.PROCESSING))
    failed_docs = sum(1 for d in docs if d.processing_status == ProcessingStatus.FAILED)
    total_chunks = sum(d.chunk_count for d in docs)

    return AdminStatsResponse(
        total_documents=total_docs,
        completed_documents=completed_docs,
        pending_documents=pending_docs,
        failed_documents=failed_docs,
        total_chunks=total_chunks,
        supported_extensions=settings.allowed_extensions,
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document_details(
    document_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve details for a specific document. Enforces Administrator role."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return DocumentRead.model_validate(doc)


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a document and cascade deletion of all its vector chunks. Enforces Administrator role."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    chunk_count = doc.chunk_count
    db.delete(doc)
    db.commit()

    return {
        "message": f"Document '{doc.title}' and {chunk_count} associated chunks deleted successfully",
        "document_id": document_id,
    }
