"""End-to-end RAG orchestrator with strict insufficient-evidence gatekeeping."""

import time
import uuid
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.user import User, UserRole
from app.models.conversation import Conversation, Message
from app.models.query_log import QueryLog
from app.schemas.chat import ChatQueryResponse, CitationSchema
from app.retrieval.vector_engine import search_vector_store
from app.rag.prompt import build_rag_prompt
from app.rag.llm import llm_client
from app.rag.citation import build_citations_from_retrieved_chunks

INSUFFICIENT_EVIDENCE_MESSAGE = (
    "I do not have sufficient information in the authorized campus documents to answer this question. "
    "Please consult the relevant campus department, registrar, or official campus directory for assistance."
)


def process_chat_query(
    db: Session,
    user: User,
    question: str,
    conversation_id: Optional[str] = None,
    top_k: Optional[int] = None,
) -> ChatQueryResponse:
    """Execute complete RAG workflow:
    1. Resolve or create conversation belonging to user.
    2. Vector search with DB-level RBAC filtering and relevance threshold.
    3. Gatekeeper: If insufficient evidence, SKIP LLM generation.
    4. If sufficient: construct prompt, call LLM, extract citations.
    5. Persist user and assistant messages.
    6. Record operational query log.
    """
    start_time = time.time()
    req_id = str(uuid.uuid4())

    # 1. Resolve or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        ).first()
        if not conversation:
            # Create new conversation with specified ID if permissible, or generate
            conversation = Conversation(id=conversation_id, user_id=user.id, title=question[:50])
            db.add(conversation)
            db.commit()
    else:
        conversation = Conversation(user_id=user.id, title=question[:50])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Persist user question message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=question,
        citations_json=None,
    )
    db.add(user_msg)
    db.commit()

    # 2. Vector search with RBAC
    retrieval_start = time.time()
    retrieved_chunks = search_vector_store(
        db=db,
        query_text=question,
        user_role=user.role,
        top_k=top_k,
    )
    retrieval_latency_ms = (time.time() - retrieval_start) * 1000.0

    # 3. Relevance Gatekeeper: Insufficient Evidence Handling
    if not retrieved_chunks:
        total_latency_ms = (time.time() - start_time) * 1000.0
        logger.info("Insufficient evidence for query: '%s'. Skipping LLM generation.", question[:60])

        # Persist assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=INSUFFICIENT_EVIDENCE_MESSAGE,
            citations_json=None,
        )
        db.add(assistant_msg)

        # Operational query log
        log_entry = QueryLog(
            request_id=req_id,
            user_id=user.id,
            user_role=user.role.value,
            question_length=len(question),
            retrieval_count=0,
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            generation_latency_ms=0.0,
            total_latency_ms=round(total_latency_ms, 2),
            outcome="insufficient_evidence",
        )
        db.add(log_entry)
        db.commit()
        db.refresh(assistant_msg)

        return ChatQueryResponse(
            answer=INSUFFICIENT_EVIDENCE_MESSAGE,
            conversation_id=conversation.id,
            message_id=assistant_msg.id,
            insufficient_evidence=True,
            citations=[],
            retrieval_count=0,
            total_latency_ms=round(total_latency_ms, 2),
        )

    # 4. Evidence exists: Construct prompt and call LLM
    generation_start = time.time()
    prompt = build_rag_prompt(question, retrieved_chunks)

    # Document summary for grounded generation
    doc_titles = list({c.document_title for c in retrieved_chunks})
    summary_str = ", ".join(doc_titles)

    answer = llm_client.generate_answer(prompt, retrieved_context_summary=summary_str)
    generation_latency_ms = (time.time() - generation_start) * 1000.0
    total_latency_ms = (time.time() - start_time) * 1000.0

    # 5. Extract and validate citations
    citations = build_citations_from_retrieved_chunks(retrieved_chunks)

    # Persist assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        citations=[c.model_dump() for c in citations],
    )
    db.add(assistant_msg)

    # 6. Operational query log
    log_entry = QueryLog(
        request_id=req_id,
        user_id=user.id,
        user_role=user.role.value,
        question_length=len(question),
        retrieval_count=len(retrieved_chunks),
        retrieval_latency_ms=round(retrieval_latency_ms, 2),
        generation_latency_ms=round(generation_latency_ms, 2),
        total_latency_ms=round(total_latency_ms, 2),
        outcome="answered",
    )
    db.add(log_entry)
    db.commit()
    db.refresh(assistant_msg)

    return ChatQueryResponse(
        answer=answer,
        conversation_id=conversation.id,
        message_id=assistant_msg.id,
        insufficient_evidence=False,
        citations=citations,
        retrieval_count=len(retrieved_chunks),
        total_latency_ms=round(total_latency_ms, 2),
    )
