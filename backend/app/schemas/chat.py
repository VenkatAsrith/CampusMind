"""Chat, RAG, and conversation schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    document_id: int = Field(..., description="Referenced document ID")
    document_title: str = Field(..., description="Document title")
    page_number: Optional[int] = Field(None, description="Page number within source document")
    section_heading: Optional[str] = Field(None, description="Heading/section of the chunk")
    chunk_id: Optional[int] = Field(None, description="Database chunk identifier")
    similarity_score: Optional[float] = Field(None, description="Similarity score of the retrieved evidence")


class ChatQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=1500,
        description="User campus question",
        json_schema_extra={"example": "When is the deadline to drop a class for fall semester?"},
    )
    conversation_id: Optional[str] = Field(None, description="Optional existing conversation UUID to continue a thread")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Override Top-K retrieval count")


class ChatQueryResponse(BaseModel):
    answer: str = Field(..., description="Synthesized answer grounded in authorized documents")
    conversation_id: str = Field(..., description="UUID of the conversation thread")
    message_id: int = Field(..., description="Generated assistant message ID")
    insufficient_evidence: bool = Field(False, description="True if no authorized documents met the relevance threshold")
    citations: List[CitationSchema] = Field(default_factory=list, description="Verified source citations from retrieved chunks")
    retrieval_count: int = Field(0, description="Number of authorized chunks retrieved")
    total_latency_ms: float = Field(0.0, description="Total request latency in milliseconds")


class MessageRead(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    citations: List[CitationSchema] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: str
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Updated conversation title")


class MentionItem(BaseModel):
    key: str
    label: str
    description: str
    required_role: str
    workflow: str


class StudentRecord(BaseModel):
    roll_number: str
    full_name: str
    email: str
    program: str
    semester: str
    academic_standing: str
    attendance_percentage: float
    registered_courses: List[str]
