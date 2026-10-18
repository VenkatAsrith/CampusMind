"""Automated test suite for advanced features:
1. Anthropic Claude provider adapter
2. Conversation rename with ownership enforcement
3. Student personal record ownership verification and horizontal escalation prevention
4. @mention commands autocomplete catalog
5. Admin Knowledge Studio stats
"""

import pytest
from app.rag.llm import LLMClient
from app.models.conversation import Conversation
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def test_anthropic_adapter_mock_generation():
    """Verify Anthropic Claude client returns grounded deterministic text in mock mode."""
    client = LLMClient()
    assert client.use_mock is True
    answer = client.generate_answer("What is the drop deadline?", retrieved_context_summary="Academic Policies 2026")
    assert "Academic Policies 2026" in answer
    assert "authorized campus documentation" in answer


def test_conversation_rename_success(client, student_user, student_headers, db_session):
    """Verify owner can successfully rename their conversation."""
    conv = Conversation(user_id=student_user.id, title="Original Title")
    db_session.add(conv)
    db_session.commit()

    response = client.patch(
        f"/api/conversations/{conv.id}",
        json={"title": "Updated Fall Schedule Questions"},
        headers=student_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Fall Schedule Questions"
    assert data["id"] == conv.id


def test_conversation_rename_cross_user_forbidden(client, student_user, faculty_headers, db_session):
    """Verify non-owner receives 403 Forbidden when attempting to rename another's conversation."""
    conv = Conversation(user_id=student_user.id, title="Student Private Thread")
    db_session.add(conv)
    db_session.commit()

    # Faculty attempts to rename student's conversation
    response = client.patch(
        f"/api/conversations/{conv.id}",
        json={"title": "Unauthorized Rename Attempt"},
        headers=faculty_headers,
    )
    assert response.status_code == 403
    assert "not authorized to modify this conversation" in response.json()["detail"]


def test_student_records_owner_access_success(client, db_session):
    """Verify student can access their own verified student record matching their username."""
    # Create individual student with roll number
    roll_user = User(
        email="23ss1a0535@campus.edu",
        username="23SS1A0535",
        full_name="Aarav Sharma",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(roll_user)
    db_session.commit()

    # Login as this student
    login_res = client.post(
        "/api/auth/login",
        json={"username": "23SS1A0535", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch own record
    res = client.get("/api/auth/student/23SS1A0535", headers=headers)
    assert res.status_code == 200
    record = res.json()
    assert record["roll_number"] == "23SS1A0535"
    assert record["full_name"] == "Aarav Sharma"
    assert "registered_courses" in record
    assert record["attendance_percentage"] > 0


def test_cross_student_record_access_strictly_forbidden(client, student_headers):
    """Verify authenticated student is strictly blocked with 403 when requesting another student's roll number."""
    # student_headers is authenticated as 'test_student'
    res = client.get("/api/auth/student/23SS1A0535", headers=student_headers)
    assert res.status_code == 403
    assert "Access Denied" in res.json()["detail"]


def test_available_mentions_endpoint(client, student_headers):
    """Verify /api/chat/mentions returns contextual suggestions without leaking unauthenticated data."""
    res = client.get("/api/chat/mentions", headers=student_headers)
    assert res.status_code == 200
    mentions = res.json()
    keys = [m["key"] for m in mentions]
    assert "help" in keys
    assert "principal" in keys


def test_admin_document_stats_endpoint(client, admin_headers):
    """Verify administrator can retrieve real knowledge-base operational metrics."""
    res = client.get("/api/admin/documents/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()
    assert "total_documents" in stats
    assert "completed_documents" in stats
    assert "total_chunks" in stats
    assert "supported_extensions" in stats


def test_student_cannot_access_admin_stats(client, student_headers):
    """Verify non-admin cannot access admin stats endpoint."""
    res = client.get("/api/admin/documents/stats", headers=student_headers)
    assert res.status_code == 403
