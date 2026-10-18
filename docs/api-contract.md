# CampusMind API Specification & Full-Stack Contract

**Author:** Principal Software Architect & Full-Stack Engineer  
**Status:** Audited, Implemented, and Verified  
**Base URL:** `http://localhost:8000/api`  
**Authentication Scheme:** HTTP Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Authentication & Identity Endpoints

### 1.1 POST `/api/auth/login`
Authenticates a student, faculty member, administrator, or executive principal and issues a signed JWT.

- **Request Body** (`application/json`):
  ```json
  {
    "username": "23SS1A0535",
    "password": "Password123!"
  }
  ```

- **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "23ss1a0535@campus.edu",
      "username": "23SS1A0535",
      "full_name": "Aarav Sharma (23SS1A0535)",
      "role": "student",
      "is_active": true,
      "created_at": "2026-10-18T12:00:00Z"
    }
  }
  ```

- **Error Responses**:
  - `401 Unauthorized`: `{"detail": "Incorrect username or password", "error_code": "AUTHENTICATION_FAILED"}`
  - `403 Forbidden`: `{"detail": "User account is inactive", "error_code": "INACTIVE_USER"}`

---

### 1.2 GET `/api/auth/me`
Retrieves the authenticated user's profile and verified server-side role.

- **Headers**: `Authorization: Bearer <token>`
- **Success Response (200 OK)**:
  ```json
  {
    "id": 1,
    "email": "23ss1a0535@campus.edu",
    "username": "23SS1A0535",
    "full_name": "Aarav Sharma (23SS1A0535)",
    "role": "student",
    "is_active": true,
    "created_at": "2026-10-18T12:00:00Z"
  }
  ```

---

### 1.3 GET `/api/auth/student/{identifier}`
Retrieves verified personal student records (enrollment, attendance, registered coursework).

- **Headers**: `Authorization: Bearer <token>`
- **Security Check**: Enforces ownership. An authenticated student may ONLY view their own records (`current_user.username == identifier`).
- **Success Response (200 OK)**:
  ```json
  {
    "roll_number": "23SS1A0535",
    "full_name": "Aarav Sharma",
    "email": "23ss1a0535@campus.edu",
    "program": "B.Tech Computer Science & Engineering",
    "semester": "Semester 6 (Academic Year 2026)",
    "academic_standing": "Good Standing (Dean's Honor Roll Eligible)",
    "attendance_percentage": 89.5,
    "registered_courses": [
      "CS301 Advanced Operating Systems",
      "CS305 Database Internals & pgvector",
      "AI310 Natural Language Processing & RAG",
      "CS312 Information Security & Cryptography"
    ]
  }
  ```
- **Error Responses**:
  - `403 Forbidden`: Attempting horizontal privilege escalation (e.g., student1 querying 23SS1A0535).
  - `401 Unauthorized`: Request missing valid Bearer token.

---

## 2. Chat, RAG, and Mentions Endpoints

### 2.1 POST `/api/chat/query`
Submits a user query. The backend executes semantic vector search with DB-level RBAC filtering. If authorized evidence meets the relevance threshold, Anthropic Claude (or fallback) generates a grounded answer with citations. If evidence is insufficient, generation is skipped and a safe refusal is returned.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body** (`application/json`):
  ```json
  {
    "question": "When is the deadline to drop classes for fall semester?",
    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "top_k": 4
  }
  ```

- **Success Response — Answered with Citations (200 OK)**:
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

- **Success Response — Insufficient Evidence (200 OK)**:
  ```json
  {
    "answer": "I do not have sufficient information in the authorized campus documents to answer this question. Please consult the relevant campus department, registrar, or official campus directory for assistance.",
    "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "message_id": 16,
    "insufficient_evidence": true,
    "citations": [],
    "retrieval_count": 0,
    "total_latency_ms": 42.1
  }
  ```

---

### 2.2 GET `/api/chat/mentions`
Returns allowable mention commands for message composer autocomplete tailored to the authenticated user's permissions.

- **Headers**: `Authorization: Bearer <token>`
- **Success Response (200 OK)**:
  ```json
  [
    {
      "key": "23SS1A0535",
      "label": "@23SS1A0535",
      "description": "View your verified enrollment, attendance, and academic standing",
      "required_role": "student",
      "workflow": "student_records"
    },
    {
      "key": "principal",
      "label": "@principal",
      "description": "Institutional administrator authorization prompt & executive records",
      "required_role": "admin",
      "workflow": "principal_elevation"
    },
    {
      "key": "help",
      "label": "@help",
      "description": "Guidelines, supported queries, citations, and platform shortcuts",
      "required_role": "student",
      "workflow": "general_help"
    }
  ]
  ```

---

## 3. Conversations Endpoints

### 3.1 GET `/api/conversations`
List all conversation threads owned by the current user.

- **Headers**: `Authorization: Bearer <token>`
- **Success Response (200 OK)**: List of `ConversationSummary`.

### 3.2 GET `/api/conversations/{conversation_id}`
Retrieve full conversation thread including user questions, assistant answers, and citations. Enforces strict user ownership (`403 Forbidden` if not owner).

### 3.3 PATCH `/api/conversations/{conversation_id}`
Update the title of an existing conversation thread. Enforces user ownership.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body** (`application/json`):
  ```json
  {
    "title": "Fall 2026 Examination Procedures"
  }
  ```
- **Success Response (200 OK)**: Updated `ConversationSummary`.

### 3.4 DELETE `/api/conversations/{conversation_id}`
Delete a conversation thread. Enforces user ownership (`403 Forbidden` if not owner).

---

## 4. Admin Knowledge Studio Endpoints

*All endpoints in this section require the `admin` role. Returns `403 Forbidden` for students or faculty.*

### 4.1 GET `/api/admin/documents/stats`
Retrieves aggregated knowledge-base metrics (total documents, indexed, pending, failed, vector chunks, supported extensions).

- **Headers**: `Authorization: Bearer <admin_token>`
- **Success Response (200 OK)**:
  ```json
  {
    "total_documents": 3,
    "completed_documents": 3,
    "pending_documents": 0,
    "failed_documents": 0,
    "total_chunks": 18,
    "supported_extensions": ["pdf", "docx", "txt"]
  }
  ```

### 4.2 POST `/api/admin/documents`
Uploads and ingests a campus document into the PostgreSQL + pgvector knowledge base.

- **Headers**: `Authorization: Bearer <admin_token>`
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Binary file (`.pdf`, `.docx`, `.txt`)
  - `audience_role`: `"student"` | `"faculty"` | `"admin"`
  - `title`: Optional custom title
- **Success Response (201 Created)**: Upload confirmation and `DocumentRead` object.

### 4.3 GET `/api/admin/documents`
Lists all documents, chunk counts, and processing status.

### 4.4 GET `/api/admin/documents/{document_id}`
Inspects document details and content hash.

### 4.5 DELETE `/api/admin/documents/{document_id}`
Cascades deletion of document and associated pgvector chunks.

---

## 5. Health Probes

- `GET /health`: Liveness probe (`{"status": "ok", "app_name": "CampusMind Backend", "version": "1.0.0"}`)
- `GET /ready`: Readiness probe verifying PostgreSQL connection, pgvector status, and embedding dimension.
