"""RAG pipeline and insufficient evidence gatekeeper tests."""

from unittest.mock import patch
from app.models.user import UserRole
from app.rag.orchestrator import process_chat_query, INSUFFICIENT_EVIDENCE_MESSAGE
from app.rag.prompt import build_rag_prompt
from app.retrieval.vector_engine import RetrievedChunk


def test_insufficient_evidence_skips_llm_call(db_session, student_user):
    """MANDATORY TEST:
    Verify that when no authorized chunks meet the relevance threshold,
    the LLM generation function is NEVER called, and the system returns
    the clear insufficient evidence refusal with 0 citations.
    """
    with patch("app.rag.llm.llm_client.generate_answer") as mock_llm_call:
        response = process_chat_query(
            db=db_session,
            user=student_user,
            question="What is the nuclear reactor launch sequence for campus?",
            conversation_id=None,
        )

        # 1. LLM MUST NEVER BE CALLED
        mock_llm_call.assert_not_called()

        # 2. Refusal response returned
        assert response.insufficient_evidence is True
        assert response.answer == INSUFFICIENT_EVIDENCE_MESSAGE
        assert len(response.citations) == 0
        assert response.retrieval_count == 0


def test_rag_prompt_injects_untrusted_context_demarcation():
    """Verify context is demarcated with untrusted tags and source attributes."""
    chunks = [
        RetrievedChunk(
            chunk_id=1,
            document_id=10,
            document_title="Campus Parking Rules",
            chunk_text="Permits required in Lot B between 8am and 5pm.",
            page_number=3,
            section_heading="Permits",
            similarity_score=0.85,
            audience_role=UserRole.STUDENT,
        )
    ]
    prompt = build_rag_prompt("Where can I park?", chunks)

    assert "<context>" in prompt
    assert "</context>" in prompt
    assert 'Source 1: "CampusParking Rules"' in prompt or 'Source 1: "Campus Parking Rules"' in prompt
    assert "Doc ID: 10, Page: 3, Section: Permits" in prompt
    assert "User Question: Where can I park?" in prompt
