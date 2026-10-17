"""API tests for administrator document management endpoints."""

import io


def test_student_upload_forbidden(client, student_headers):
    """Verify students cannot upload documents."""
    files = {"file": ("student_guide.txt", io.BytesIO(b"Sample student guide content"), "text/plain")}
    response = client.post(
        "/api/admin/documents",
        files=files,
        data={"audience_role": "student"},
        headers=student_headers,
    )
    assert response.status_code == 403


def test_admin_upload_document_success(client, admin_headers):
    """Verify administrator can upload a document and it gets processed and chunked."""
    doc_content = b"# Campus Library Policy\nThe campus library is open 24/7 during finals week."
    files = {"file": ("library_policy.txt", io.BytesIO(doc_content), "text/plain")}
    response = client.post(
        "/api/admin/documents",
        files=files,
        data={"audience_role": "student", "title": "Library Policy 2026"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["document"]["title"] == "Library Policy 2026"
    assert data["document"]["processing_status"] == "completed"
    assert data["document"]["chunk_count"] >= 1
    doc_id = data["document"]["id"]

    # Verify listing includes the uploaded document
    list_res = client.get("/api/admin/documents", headers=admin_headers)
    assert list_res.status_code == 200
    assert any(d["id"] == doc_id for d in list_res.json()["documents"])

    # Verify deletion
    del_res = client.delete(f"/api/admin/documents/{doc_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["document_id"] == doc_id


def test_admin_upload_unsupported_file_fails(client, admin_headers):
    """Verify administrator upload of unsupported file type (.exe) is rejected."""
    files = {"file": ("malicious.exe", io.BytesIO(b"fake payload"), "application/octet-stream")}
    response = client.post(
        "/api/admin/documents",
        files=files,
        data={"audience_role": "student"},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
