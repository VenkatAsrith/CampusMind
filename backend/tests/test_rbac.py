"""Unit tests proving Role-Based Access Control and authorization enforcement."""

from app.models.user import UserRole
from app.api.dependencies import get_authorized_roles, ROLE_HIERARCHY


def test_rbac_authorized_roles_mapping():
    """Verify strictly defined retrieval clearance levels:
    - Student: only student documents
    - Faculty: student + faculty documents
    - Admin: student + faculty + admin documents
    """
    student_roles = get_authorized_roles(UserRole.STUDENT)
    assert student_roles == [UserRole.STUDENT]
    assert UserRole.FACULTY not in student_roles
    assert UserRole.ADMIN not in student_roles

    faculty_roles = get_authorized_roles(UserRole.FACULTY)
    assert set(faculty_roles) == {UserRole.STUDENT, UserRole.FACULTY}
    assert UserRole.ADMIN not in faculty_roles

    admin_roles = get_authorized_roles(UserRole.ADMIN)
    assert set(admin_roles) == {UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN}


def test_role_hierarchy_numeric_ordering():
    """Verify that student < faculty < admin."""
    assert ROLE_HIERARCHY[UserRole.STUDENT] < ROLE_HIERARCHY[UserRole.FACULTY]
    assert ROLE_HIERARCHY[UserRole.FACULTY] < ROLE_HIERARCHY[UserRole.ADMIN]


def test_student_cannot_access_admin_document_endpoints(client, student_headers):
    """Verify student gets 403 Forbidden when calling document management."""
    response = client.get("/api/admin/documents", headers=student_headers)
    assert response.status_code == 403
    assert "Operation requires minimum role of 'admin'" in response.json()["detail"]


def test_faculty_cannot_access_admin_document_endpoints(client, faculty_headers):
    """Verify faculty gets 403 Forbidden when calling admin document management."""
    response = client.get("/api/admin/documents", headers=faculty_headers)
    assert response.status_code == 403
    assert "Operation requires minimum role of 'admin'" in response.json()["detail"]


def test_admin_can_access_document_endpoints(client, admin_headers):
    """Verify admin gets 200 OK when accessing document management."""
    response = client.get("/api/admin/documents", headers=admin_headers)
    assert response.status_code == 200
    assert "documents" in response.json()
