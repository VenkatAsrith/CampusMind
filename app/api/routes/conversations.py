"""Conversations API routes enforcing strict ownership checks."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.chat import ConversationRead, ConversationSummary, MessageRead, CitationSchema
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationSummary])
def list_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all conversations owned by the authenticated user."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
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


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full conversation thread and messages. Enforces strict user ownership."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Strictly verify ownership
    if conv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this conversation",
        )

    messages = []
    for m in conv.messages:
        citations = []
        for c in m.citations:
            try:
                citations.append(CitationSchema(**c))
            except Exception:
                pass
        messages.append(
            MessageRead(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                citations=citations,
                created_at=m.created_at,
            )
        )

    return ConversationRead(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages,
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a conversation thread. Enforces user ownership."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this conversation",
        )

    db.delete(conv)
    db.commit()
    return {"message": "Conversation successfully deleted", "conversation_id": conversation_id}
