"""Chat query and conversation retrieval routes."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ConversationSummary
from app.api.dependencies import get_current_user
from app.rag.orchestrator import process_chat_query

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])


@router.post("/query", response_model=ChatQueryResponse)
def chat_query(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute authenticated RAG query with DB-level RBAC filtering and citation generation."""
    return process_chat_query(
        db=db,
        user=current_user,
        question=request.question,
        conversation_id=request.conversation_id,
        top_k=request.top_k,
    )


@router.get("/history", response_model=List[ConversationSummary])
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
):
    """Retrieve conversation history owned by the currently authenticated user."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .all()
    )
    return [
        ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages),
        )
        for c in convs
    ]
