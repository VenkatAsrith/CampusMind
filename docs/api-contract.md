# CampusMind API Specification & Teammate Contract

**Author:** Person 2 (Backend & AI/RAG Engineer)  
**Consumer:** Person 1 (Frontend & UX Engineer) & Person 3 (DevOps/QA Engineer)  
**Base URL:** `http://localhost:8000/api`  
**Authentication Scheme:** HTTP Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Authentication Endpoints

### 1.1 POST `/api/auth/login`
Authenticates a student, faculty member, or administrator and issues a JWT token.

- **Request Body** (`application/json`):
  ```json
  {
    "username": "student1",
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
      "email": "student1@campus.edu",
      "username": "student1",
      "full_name": "Alex Student",
      "role": "student",
      "is_active": true,
      "created_at": "2026-10-17T12:00:00Z"
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
    "email": "student1@campus.edu",
    "username": "student1",
    "full_name": "Alex Student",
    "role": "student",
    "is_active": true,
    "created_at": "2026-10-17T12:00:00Z"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Token missing, expired, or invalid.

---

## 2. Chat & RAG Endpoints

### 2.1 POST `/api/chat/query`
Submits a user query. The backend executes semantic vector search with DB-level RBAC filtering. If authorized evidence meets the relevance threshold, the LLM generates a grounded answer with citations. If evidence is insufficient, LLM generation is skipped and a safe refusal is returned.

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

### 2.2 GET `/api/chat/history`
Returns recent conversation summaries belonging to the authenticated user.

- **Headers**: `Authorization: Bearer <token>`
- **Query Params**: `limit=50`
- **Success Response (200 OK)**:
  ```json
  [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "When is the deadline to drop classes...",
      "created_at": "2026-10-17T12:10:00Z",
      "updated_at": "2026-10-17T12:12:00Z",
      "message_count": 4
    }
  ]
  ```

---

## 3. Conversations Endpoints

### 3.1 GET `/api/conversations`
List all conversation threads for current user.

- **Headers**: `Authorization: Bearer <token>`
- **Response**: List of `ConversationSummary`.

### 3.2 GET `/api/conversations/{conversation_id}`
Retrieve a full conversation thread including user questions, assistant answers, and citations.

- **Headers**: `Authorization: Bearer <token>`
- **Security Check**: Enforces ownership. Returns `403 Forbidden` if another user attempts access.
- **Success Response (200 OK)**:
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "user_id": 1,
    "title": "Drop Deadlines",
    "created_at": "2026-10-17T12:10:00Z",
    "updated_at": "2026-10-17T12:12:00Z",
    "messages": [
      {
        "id": 1,
        "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "role": "user",
        "content": "When can I drop classes?",
        "citations": [],
        "created_at": "2026-10-17T12:10:00Z"
      },
      {
        "id": 2,
        "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "role": "assistant",
        "content": "The deadline is September 8, 2026.",
        "citations": [
          {
            "document_id": 1,
            "document_title": "Academic Calendar 2026",
            "page_number": 1,
            "section_heading": "Deadlines",
            "chunk_id": 4,
            "similarity_score": 0.89
          }
        ],
        "created_at": "2026-10-17T12:10:05Z"
      }
    ]
  }
  ```

### 3.3 DELETE `/api/conversations/{conversation_id}`
Delete a conversation thread. Enforces user ownership (`403 Forbidden` if not owner).

---

## 4. Admin Document Management Endpoints

*All endpoints in this group require the `admin` role. Returns `403 Forbidden` for students or faculty.*

### 4.1 POST `/api/admin/documents`
Uploads and ingests a campus document into the PostgreSQL + pgvector knowledge base.

- **Headers**: `Authorization: Bearer <admin_token>`
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Binary file (`.pdf`, `.docx`, `.txt`)
  - `audience_role`: `"student"` | `"faculty"` | `"admin"` (default `"student"`)
  - `title`: Optional custom document title string
- **Success Response (201 Created)**:
  ```json
  {
    "message": "Document 'Library Guidelines' uploaded and processed successfully",
    "document": {
      "id": 5,
      "filename": "library_guidelines.pdf",
      "title": "Library Guidelines",
      "document_type": "pdf",
      "file_size_bytes": 104230,
      "content_hash": "c5f891b...",
      "uploader_id": 3,
      "audience_role": "student",
      "processing_status": "completed",
      "error_message": null,
      "chunk_count": 8,
      "created_at": "2026-10-17T12:30:00Z",
      "updated_at": "2026-10-17T12:30:02Z"
    }
  }
  ```

### 4.2 GET `/api/admin/documents`
Lists all documents, chunk counts, and processing status.

### 4.3 GET `/api/admin/documents/{document_id}`
Inspects document details.

### 4.4 DELETE `/api/admin/documents/{document_id}`
Deletes document and cascades chunk deletions.

---

## 5. Health & Monitoring Probes

- `GET /health`: Liveness probe (`{"status": "ok", "app_name": "CampusMind Backend", "version": "1.0.0"}`)
- `GET /ready`: Readiness probe verifying PostgreSQL connection, pgvector status, and embedding dimension.
