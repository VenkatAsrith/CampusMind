# CampusMind Three-Person Team Integration Checklist

**Owner (Author):** Person 2 (Backend Engineering + AI/RAG + Database + Security + Testing)  
**Teammates:**  
- **Person 1:** Frontend & UX (React, User Interface, Chat UI, Citation Rendering, Admin Dashboard)  
- **Person 3:** DevOps, QA & Deployment (Docker, CI/CD, Production PostgreSQL + pgvector, Monitoring)  

---

## 1. Person 1 — Frontend Integration Specifications

### 1.1 Authentication & Session
- **Login Endpoint:** `POST /api/auth/login`
- **Request Format:** JSON `{ "username": "<username_or_email>", "password": "<plain_password>" }`
- **Response Format:** JSON containing `access_token`, `token_type` ("bearer"), and `user` object (`id`, `username`, `email`, `full_name`, `role`).
- **Storage:** Frontend should store `access_token` in memory or secure storage and include it on every protected request as:
  `Authorization: Bearer <access_token>`
- **Current User Profile:** `GET /api/auth/me` validates the token and returns the current role.
- **Client-Side Authorization:** Frontend can render conditional UI views based on `user.role`, but **backend strictly enforces RBAC server-side on every route and retrieval query**.

### 1.2 Chat Interface & Citations Rendering
- **Chat Query Endpoint:** `POST /api/chat/query`
- **Request Format:**
  ```json
  {
    "question": "When can students drop classes?",
    "conversation_id": "optional-uuid-to-continue-thread"
  }
  ```
- **Response Format:**
  ```json
  {
    "answer": "The official drop deadline for undergraduate students is September 8, 2026.",
    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "message_id": 15,
    "insufficient_evidence": false,
    "citations": [
      {
        "document_id": 1,
        "document_title": "Campus Academic Calendar & Policies 2026",
        "page_number": 1,
        "section_heading": "Add/Drop Policies",
        "chunk_id": 12,
        "similarity_score": 0.8842
      }
    ],
    "retrieval_count": 1,
    "total_latency_ms": 320.5
  }
  ```
- **Insufficient Evidence Handling:** If `insufficient_evidence: true`, frontend should display the polite refusal message and show no citations badge.

### 1.3 Administrator Knowledge Dashboard
- **Upload Document:** `POST /api/admin/documents` (multipart/form-data with `file`, `audience_role`, `title`)
- **List Documents:** `GET /api/admin/documents`
- **Delete Document:** `DELETE /api/admin/documents/{id}`
- **Security:** If non-admin attempts these endpoints, the backend returns HTTP 403 Forbidden with `{ "detail": "Operation requires minimum role of 'admin'", "error_code": "PERMISSION_DENIED" }`.

---

## 2. Person 3 — DevOps & Deployment Integration Specifications

### 2.1 Containerization
- **Dockerfile:** Provided at repository root. Uses Python 3.12-slim, non-root user `campusmind` (UID 1001), and standard healthcheck probe.
- **Docker Compose:** `docker-compose.yml` provides orchestrated multi-container deployment:
  - `postgres`: Image `pgvector/pgvector:pg16` with healthcheck on port 5432.
  - `backend`: Depends on postgres healthy state, exposes FastAPI on port 8000.

### 2.2 Database Initialization & Migrations
- Extension requirement: `CREATE EXTENSION IF NOT EXISTS vector;` (automatically verified in `init_database()`).
- Seed script: `python -m app.db.init_db` initializes tables and default accounts for testing.
- PostgreSQL Connection string format:
  `postgresql+psycopg2://<user>:<password>@<host>:5432/<dbname>`

### 2.3 Probes for Kubernetes / Container Orchestrators
- **Liveness Probe:** `GET /health` -> `200 OK` (`{"status": "ok", "app_name": "CampusMind Backend"}`)
- **Readiness Probe:** `GET /ready` -> `200 OK` (`{"status": "ready", "database": "connected", "vector_support": true, "embedding_dimension": 384}`)

### 2.4 Mandatory Environment Variables
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `LLM_API_KEY` (if using hosted live LLM)
- `ALLOWED_CORS_ORIGINS` (comma-separated frontend URLs)

---

## 3. Verified Integration Status

| Requirement | Responsible Party | Status | Verification Evidence |
|---|---|---|---|
| REST API Contracts | Person 2 -> Person 1 | **Verified** | Documented in `docs/api-contract.md`; tested via 33 automated tests. |
| CORS Header Configuration | Person 2 -> Person 1 | **Verified** | Configured via `settings.ALLOWED_CORS_ORIGINS` and FastAPI CORSMiddleware. |
| Role-Based Route Protection | Person 2 | **Verified** | `test_rbac.py` passes: students/faculty blocked from admin endpoints. |
| DB-Level RBAC in Retrieval | Person 2 | **Verified** | `test_retrieval.py` passes: student queries cannot retrieve faculty/admin chunks. |
| Non-Root Docker Image | Person 2 -> Person 3 | **Verified** | `Dockerfile` creates unprivileged UID 1001 user and sets `USER campusmind`. |
| Docker Compose Setup | Person 2 -> Person 3 | **Verified** | `docker-compose.yml` configures `pgvector/pgvector:pg16` + `backend`. |
| Automated Test Suite | Person 2 | **Verified** | 33 passed, 0 failed in `pytest`. |
