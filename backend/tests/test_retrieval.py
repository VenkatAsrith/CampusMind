"""Unit and retrieval tests verifying similarity calculations and DB-level RBAC filtering."""

import pytest
from app.models.user import UserRole
from app.models.document import Document, ProcessingStatus
from app.models.chunk import DocumentChunk
from app.embeddings.service import embedding_service
from app.retrieval.vector_engine import (
    compute_cosine_similarity,
    search_vector_store,
)


def test_cosine_similarity_calculation():
    """Verify cosine similarity mathematical properties:
    - Identical vectors have similarity 1.0
    - Orthogonal vectors have similarity 0.0
    - Opposite vectors have similarity -1.0
    """
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    v4 = [-1.0, 0.0, 0.0]

    assert pytest.approx(compute_cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(compute_cosine_similarity(v1, v3), 0.001) == 0.0
    assert pytest.approx(compute_cosine_similarity(v1, v4), 0.001) == -1.0


def test_retrieval_enforces_student_clearance(db_session, admin_user):
    """CRITICAL SECURITY TEST:
    Insert 3 documents (Student, Faculty, Admin).
    Verify that a Student query CANNOT retrieve Faculty or Admin chunks.
    """
    # 1. Create Student Doc & Chunk
    doc_student = Document(
        filename="student_doc.txt",
        title="Student Syllabus Guide",
        document_type="txt",
        content_hash="hash_student",
        uploader_id=admin_user.id,
        audience_role=UserRole.STUDENT,
        processing_status=ProcessingStatus.COMPLETED,
    )
    db_session.add(doc_student)
    db_session.commit()
    db_session.refresh(doc_student)

    student_text = "Drop deadline is the second Friday of classes."
    chunk_student = DocumentChunk(
        document_id=doc_student.id,
        chunk_index=0,
        chunk_text=student_text,
        audience_role=UserRole.STUDENT,
        embedding=embedding_service.embed_text(student_text),
    )
    db_session.add(chunk_student)

    # 2. Create Faculty Doc & Chunk
    doc_faculty = Document(
        filename="faculty_doc.txt",
        title="Faculty Salary Committee Minutes",
        document_type="txt",
        content_hash="hash_faculty",
        uploader_id=admin_user.id,
        audience_role=UserRole.FACULTY,
        processing_status=ProcessingStatus.COMPLETED,
    )
    db_session.add(doc_faculty)
    db_session.commit()
    db_session.refresh(doc_faculty)

    faculty_text = "Confidential faculty peer evaluations and merit increase decisions."
    chunk_faculty = DocumentChunk(
        document_id=doc_faculty.id,
        chunk_index=0,
        chunk_text=faculty_text,
        audience_role=UserRole.FACULTY,
        embedding=embedding_service.embed_text(faculty_text),
    )
    db_session.add(chunk_faculty)

    # 3. Create Admin Doc & Chunk
    doc_admin = Document(
        filename="admin_doc.txt",
        title="Administrative Encryption Keys",
        document_type="txt",
        content_hash="hash_admin",
        uploader_id=admin_user.id,
        audience_role=UserRole.ADMIN,
        processing_status=ProcessingStatus.COMPLETED,
    )
    db_session.add(doc_admin)
    db_session.commit()
    db_session.refresh(doc_admin)

    admin_text = "Master administrative credentials and facility alarm overrides."
    chunk_admin = DocumentChunk(
        document_id=doc_admin.id,
        chunk_index=0,
        chunk_text=admin_text,
        audience_role=UserRole.ADMIN,
        embedding=embedding_service.embed_text(admin_text),
    )
    db_session.add(chunk_admin)
    db_session.commit()

    # TEST A: Query as STUDENT
    results_student = search_vector_store(
        db=db_session,
        query_text="confidential evaluations and alarm credentials",
        user_role=UserRole.STUDENT,
        similarity_threshold=-1.0,  # capture all matching role chunks regardless of score
    )
    retrieved_roles_student = [c.audience_role for c in results_student]
    assert all(r == UserRole.STUDENT for r in retrieved_roles_student)
    assert UserRole.FACULTY not in retrieved_roles_student
    assert UserRole.ADMIN not in retrieved_roles_student

    # TEST B: Query as FACULTY
    results_faculty = search_vector_store(
        db=db_session,
        query_text="confidential evaluations and alarm credentials",
        user_role=UserRole.FACULTY,
        similarity_threshold=-1.0,
    )
    retrieved_roles_faculty = [c.audience_role for c in results_faculty]
    assert UserRole.ADMIN not in retrieved_roles_faculty
    assert any(r == UserRole.FACULTY for r in retrieved_roles_faculty)

    # TEST C: Query as ADMIN
    results_admin = search_vector_store(
        db=db_session,
        query_text="confidential evaluations and alarm credentials",
        user_role=UserRole.ADMIN,
        similarity_threshold=-1.0,
    )
    retrieved_roles_admin = [c.audience_role for c in results_admin]
    assert any(r == UserRole.ADMIN for r in retrieved_roles_admin)
