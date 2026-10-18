"""Chat query and conversation retrieval routes."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ConversationSummary, MentionItem
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


@router.get("/mentions", response_model=List[MentionItem])
def get_available_mentions(current_user: User = Depends(get_current_user)):
    """Return available @-mention actions tailored to authenticated user context."""
    mentions = [
        MentionItem(
            key="help",
            label="@help",
            description="Guidelines, supported queries, citations, and platform shortcuts",
            required_role="student",
            workflow="general_help",
        ),
        MentionItem(
            key="principal",
            label="@principal",
            description="Institutional administrator authorization prompt & executive records",
            required_role="admin",
            workflow="principal_elevation",
        ),
    ]

    # Student personal record mention
    if current_user.role == UserRole.STUDENT:
        mentions.insert(
            0,
            MentionItem(
                key=current_user.username,
                label=f"@{current_user.username}",
                description="View your verified enrollment, attendance, and academic standing",
                required_role="student",
                workflow="student_records",
            ),
        )
    else:
        mentions.insert(
            0,
            MentionItem(
                key="student",
                label="@student",
                description="Lookup student verified profile (requires authorized identity)",
                required_role="student",
                workflow="student_lookup",
            ),
        )

    return mentions
