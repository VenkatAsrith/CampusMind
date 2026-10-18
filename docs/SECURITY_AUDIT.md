# CampusMind Security Audit & Hardening Report

**Audit Date:** October 2026  
**Auditor:** Principal Application Security Engineer  
**Scope:** Full-Stack Architecture (`backend/` FastAPI + pgvector, `frontend/` React/TypeScript, AI RAG Pipeline)

---

## 1. Executive Summary

CampusMind was audited against the OWASP Top 10, the OWASP API Security Top 10, and AI/LLM Security standards. The system enforces **defense-in-depth**, **least privilege**, and **default-deny authorization**. All authorization and identity decisions are strictly resolved server-side.

---

## 2. Authentication & Credential Security

| Control | Status | Implementation Details |
|---|---|---|
| **Password Hashing** | Passed | Uses **Argon2id** via `argon2-cffi` and `passlib`. Plaintext passwords are never persisted. |
| **JWT Signature & Claims** | Passed | Signed with HS256 using configurable `JWT_SECRET_KEY`. Validates `exp` timestamp and subject identity on every request. |
| **Inactive User Enforcement** | Passed | The `get_current_user` dependency immediately rejects inactive accounts with HTTP 401/403. |
| **Credential Masking** | Passed | Secret credentials (`ANTHROPIC_API_KEY`, `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`) are isolated in backend environment variables and never exposed to the frontend or build bundles. |
| **Timing-Attack Resilience** | Passed | Password verification uses constant-time comparison algorithms in Argon2/passlib. |

---

## 3. Authorization & Privilege Escalation Prevention

### 3.1 Role-Based Access Control (RBAC) Matrix
The three-tier role hierarchy is enforced in backend route dependencies (`require_admin`, `require_faculty`, `require_student`):
- **Student**: Access to student/public campus documentation. No document ingestion or admin endpoints.
- **Faculty**: Access to faculty and student documentation. No administrative document ingestion.
- **Admin**: Full knowledge base management, file ingestion, and cascade deletion.

### 3.2 Horizontal Privilege Escalation Protection
- **Conversations**: Every conversation lookup (`GET`, `PATCH`, `DELETE` on `/api/conversations/{id}`) validates `conv.user_id == current_user.id`. Requests by other users return `403 Forbidden`.
- **Student Personal Records**: In `/api/auth/student/{identifier}`, student accounts can **only** inspect records matching their own authenticated `username` (roll number). Cross-student inspection attempts are rejected with `403 Forbidden` and logged.

### 3.3 @ Mention Workflow Security
Typing `@student`, `@<roll_number>`, or `@principal` in the user interface is strictly a UX autocomplete convenience. The backend verifies authentic credentials on every query. Typing `@principal` cannot elevate permissions without authenticating a server-verified administrator account.

---

## 4. Vector Retrieval & AI Context Isolation

### 4.1 SQL/pgvector DB-Level Filtering
Retrieval-time authorization is applied directly within the database query:
```sql
SELECT c.chunk_text, (1 - (c.embedding <=> :query_vector::vector)) AS similarity
FROM document_chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.audience_role = ANY(:roles)
  AND d.processing_status = 'completed'
  AND (c.embedding <=> :query_vector::vector) <= :max_distance
ORDER BY c.embedding <=> :query_vector::vector ASC
LIMIT :top_k;
```
Restricted evidence **never enters application memory or LLM prompt context**, preventing prompt injection leaks or indirect context leakage.

### 4.2 Insufficient Evidence Gatekeeper
If no authorized document meets the relevance threshold (`SIMILARITY_THRESHOLD >= 0.30`), the orchestrator **skips the LLM network call entirely**, returning a verified safe refusal message and avoiding hallucinations.

---

## 5. Input Validation & Document Ingestion Security

- **Path Traversal Prevention**: Uploaded filenames are sanitized (`os.path.basename` and regex stripping) to prevent directory traversal attacks.
- **MIME & Extension Whitelist**: Only `.pdf`, `.docx`, and `.txt` extensions are accepted.
- **File Size Quotas**: Upload sizes are capped at 10 MB (`MAX_UPLOAD_SIZE_BYTES = 10485760`).
- **Prompt Injection Demarcation**: Retrieved chunks are wrapped inside demarcated XML blocks (`<context>` ... `</context>`) with explicit instructions to the LLM to treat retrieved text as untrusted reference material.

---

## 6. Audit Verdict

**Production Status: Approved.** All negative tests, tamper checks, and cross-user isolation tests passed successfully.
