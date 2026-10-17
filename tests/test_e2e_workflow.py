"""End-to-end comprehensive integration workflow test.

Simulates the complete 16-step campus workflow:
1. Authenticate as Administrator
2. Upload sample campus document
3. Verify extraction, chunking, and metadata
4. Authenticate as Student
5. Ask question answerable from document
6. Verify retrieval and source citation
7. Ask unsupported question -> verify insufficient evidence and LLM skipped
8. Attempt student access to faculty/admin restricted content -> access denied
9. Verify conversation history & cross-user privacy isolation
"""

import io
from unittest.mock import patch
from app.models.user import UserRole
from app.rag.orchestrator import INSUFFICIENT_EVIDENCE_MESSAGE


def test_complete_campusmind_e2e_workflow(
    client,
    admin_headers,
    student_headers,
    faculty_headers,
):
    # Step 1 & 2: Administrator uploads public academic calendar policy
    doc_text = (
        "# Campus Academic Calendar\n"
        "The official drop deadline for all undergraduate students is September 8, 2026.\n"
        "Tuition payments must be finalized by September 15, 2026.\n"
    ).encode("utf-8")

    upload_res = client.post(
        "/api/admin/documents",
        files={"file": ("academic_calendar.txt", io.BytesIO(doc_text), "text/plain")},
        data={"audience_role": "student", "title": "Academic Calendar 2026"},
        headers=admin_headers,
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()["document"]
    doc_id = doc_data["id"]

    # Step 3, 4, 5: Verify extraction, chunk count
    assert doc_data["processing_status"] == "completed"
    assert doc_data["chunk_count"] >= 1

    # Step 6 & 7: Student asks question answerable from the document
    with patch("app.rag.llm.llm_client.generate_answer") as mock_llm:
        mock_llm.return_value = "The official drop deadline for undergraduate students is September 8, 2026."

        query_payload = {"question": "When is the official drop deadline for classes?"}
        chat_res = client.post("/api/chat/query", json=query_payload, headers=student_headers)

        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        student_conv_id = chat_data["conversation_id"]

        # Step 8 & 9: Verify answer and verified citations
        assert chat_data["insufficient_evidence"] is False
        assert "September 8, 2026" in chat_data["answer"]
        assert len(chat_data["citations"]) >= 1
        assert chat_data["citations"][0]["document_title"] == "Academic Calendar 2026"
        assert chat_data["citations"][0]["document_id"] == doc_id

    # Step 10, 11, 12: Ask an unsupported question
    with patch("app.rag.llm.llm_client.generate_answer") as mock_llm_unsupported:
        unsupported_query = {"question": "What is the secret recipe for cafeteria lasagna?"}
        unsupported_res = client.post("/api/chat/query", json=unsupported_query, headers=student_headers)

        assert unsupported_res.status_code == 200
        unsupported_data = unsupported_res.json()

        # Generation MUST be skipped and refusal returned
        mock_llm_unsupported.assert_not_called()
        assert unsupported_data["insufficient_evidence"] is True
        assert unsupported_data["answer"] == INSUFFICIENT_EVIDENCE_MESSAGE
        assert len(unsupported_data["citations"]) == 0

    # Step 13 & 14: Attempt to access restricted administrative documents as student
    unauth_doc_req = client.get("/api/admin/documents", headers=student_headers)
    assert unauth_doc_req.status_code == 403

    unauth_del_req = client.delete(f"/api/admin/documents/{doc_id}", headers=student_headers)
    assert unauth_del_req.status_code == 403

    # Step 15 & 16: Verify conversation history and cross-user privacy
    history_res = client.get("/api/chat/history", headers=student_headers)
    assert history_res.status_code == 200
    assert any(c["id"] == student_conv_id for c in history_res.json())

    # Faculty tries to access student conversation
    snoop_res = client.get(f"/api/conversations/{student_conv_id}", headers=faculty_headers)
    assert snoop_res.status_code == 403
