"""API tests for chat queries, conversations, and health endpoints."""

import io


def test_health_and_readiness_endpoints(client):
    """Verify health and readiness probes return 200 OK."""
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"

    ready_res = client.get("/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"


def test_cross_user_conversation_isolation(client, student_headers, faculty_headers):
    """MANDATORY PRIVACY TEST:
    Verify that user A (faculty) cannot view or delete conversation owned by user B (student).
    """
    # 1. Student creates a conversation via chat query
    query_payload = {"question": "What are the lab hours?"}
    chat_res = client.post("/api/chat/query", json=query_payload, headers=student_headers)
    assert chat_res.status_code == 200
    conv_id = chat_res.json()["conversation_id"]

    # 2. Student can retrieve their own conversation
    student_get = client.get(f"/api/conversations/{conv_id}", headers=student_headers)
    assert student_get.status_code == 200
    assert student_get.json()["id"] == conv_id

    # 3. Faculty attempts to retrieve Student's conversation -> MUST RETURN 403 FORBIDDEN
    faculty_get = client.get(f"/api/conversations/{conv_id}", headers=faculty_headers)
    assert faculty_get.status_code == 403
    assert "not authorized" in faculty_get.json()["detail"]

    # 4. Faculty attempts to delete Student's conversation -> MUST RETURN 403 FORBIDDEN
    faculty_del = client.delete(f"/api/conversations/{conv_id}", headers=faculty_headers)
    assert faculty_del.status_code == 403


def test_chat_query_validation(client, student_headers):
    """Verify empty or single-character question is rejected by schema validation."""
    response = client.post("/api/chat/query", json={"question": "a"}, headers=student_headers)
    assert response.status_code == 422  # Pydantic validation error
