"""Document management schemas for administrators and metadata inspection."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole
from app.models.document import ProcessingStatus


class DocumentRead(BaseModel):
    id: int
    filename: str
    title: str
    document_type: str
    file_size_bytes: int
    content_hash: str
    uploader_id: int
    audience_role: UserRole
    processing_status: ProcessingStatus
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentRead


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentRead]


class ChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    chunk_text: str
    page_number: Optional[int]
    section_heading: Optional[str]
    audience_role: UserRole

    model_config = {"from_attributes": True}
