# CampusMind Backend — Comprehensive Repository Audit & Architectural Assessment

**Auditor:** Person 2 (Senior Backend Engineer & AI/RAG Architect)  
**Date:** Phase 1 / Phase Zero Repository Audit  
**Workspace:** `f:\PROJECTS\CampusMind\campusmind-backend`

---

## 1. Executive Summary

CampusMind is an AI-powered campus information assistant designed to provide trusted, grounded answers using authorized campus documentation. The system mandates a three-tier Role-Based Access Control (RBAC) model:
- **Student**: General student body access (syllabi, campus schedules, public policies, tuition deadlines).
- **Faculty**: Faculty and departmental access (faculty handbooks, department grading guidelines, academic committee notes, student documents).
- **Administrator**: Full administrative access (institutional governance, personnel guidelines, all documents, ingestion and deletion management).

This audit establishes the baseline state of the repository, analyzes dependency requirements, evaluates system prerequisites (PostgreSQL with pgvector, Python environment, embedding models, and LLM APIs), and defines the architectural blueprint to satisfy all prompt requirements.

---

## 2. Repository & Workspace State

- **Current Repository Directory**: `f:\PROJECTS\CampusMind\campusmind-backend`
- **Current State**: Initialized repository workspace.
- **Existing Content**:
  - `README.md` (Created and linking to Person 2 Master Prompt)
  - `docs/README_PERSON2_MASTER_PROMPT.md` (Verbatim master prompt verified)
  - `docs/backend-implementation-status.md` (Implementation progress tracking)
- **Version Control**: Git status checked. Clean workspace ready for modular backend foundation.
- **Host Environment**: Windows PowerShell, Python 3.12.10, pip 26.1.2.

---

## 3. Technology Stack & Component Evaluation

| Subsystem | Intended Technology | Rationale & Requirements |
|---|---|---|
| **Web Framework** | **FastAPI** (Python 3.12) | Asynchronous, high-performance, OpenAPI/Swagger generation, Pydantic v2 validation. |
| **Database** | **PostgreSQL** + **pgvector** | Relational integrity for users, conversations, documents + native vector similarity indexing (`HNSW` / `IVFFlat`). |
| **ORM & Migrations** | **SQLAlchemy 2.0** + **Alembic** | Modern typed ORM, transactional safety, reproducible database schema migrations. |
| **Embeddings** | **Sentence-Transformers** (`all-MiniLM-L6-v2`) | Compact (384-dimensional), fast inference, strong semantic retrieval on academic/campus text. |
| **LLM Orchestration** | Hosted LLM Client (OpenAI/Groq/LiteLLM/HuggingFace compatible) | Grounded context prompting, strict evidence-only synthesis, temperature 0.0 for factual fidelity. |
| **Authentication** | **JWT (python-jose / PyJWT)** + **Argon2id/Passlib/Bcrypt** | Industry standard, tamper-proof role claims, salted hash verification, token expiry. |
| **Authorization** | Server-side **RBAC** dependency injection | Never trust client-supplied roles; enforce permissions at route and vector retrieval levels. |
| **Document Ingestion** | `pypdf`, `python-docx`, text extractors | Multi-format parsing, structural sectioning, sliding chunker with metadata preservation. |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` | Comprehensive unit tests, vector similarity tests, mock LLM/embedding fixtures, E2E flows. |

---

## 4. Analysis of Required Architecture & Entities

### 4.1 Database Entities & Schemas
1. **Users (`users`)**:
   - `id` (UUID/Integer, PK)
   - `email` (Unique, indexed)
   - `username` (Unique, indexed)
   - `hashed_password` (Salted hash)
   - `full_name` (String)
   - `role` (`student`, `faculty`, `admin`)
   - `is_active` (Boolean)
   - `created_at`, `updated_at` (Timestamps)

2. **Documents (`documents`)**:
   - `id` (UUID/Integer, PK)
   - `filename`, `title` (String)
   - `document_type` (`pdf`, `docx`, `txt`)
   - `file_size_bytes` (Integer)
   - `content_hash` (SHA-256 for deduplication)
   - `uploader_id` (FK to `users.id`)
   - `audience_role` (`student`, `faculty`, `admin` — defines minimum clearance required)
   - `processing_status` (`pending`, `processing`, `completed`, `failed`)
   - `error_message` (Text, nullable)
   - `chunk_count` (Integer)
   - `created_at`, `updated_at` (Timestamps)

3. **Document Chunks (`document_chunks`)**:
   - `id` (UUID/Integer, PK)
   - `document_id` (FK to `documents.id`, `ON DELETE CASCADE`)
   - `chunk_index` (Integer)
   - `chunk_text` (Text)
   - `page_number` (Integer, nullable)
   - `section_heading` (String, nullable)
   - `audience_role` (`student`, `faculty`, `admin` — denormalized for vector query filtering)
   - `embedding` (`VECTOR(384)`)
   - `created_at` (Timestamp)

4. **Conversations (`conversations`)**:
   - `id` (UUID, PK)
   - `user_id` (FK to `users.id`, `ON DELETE CASCADE`)
   - `title` (String)
   - `created_at`, `updated_at` (Timestamps)

5. **Messages (`messages`)**:
   - `id` (UUID, PK)
   - `conversation_id` (FK to `conversations.id`, `ON DELETE CASCADE`)
   - `role` (`user`, `assistant`, `system`)
   - `content` (Text)
   - `citations` (JSONB: document titles, ids, page numbers, sections)
   - `created_at` (Timestamp)

6. **Query Logs (`query_logs`)**:
   - `id` (UUID, PK)
   - `request_id` (UUID/String)
   - `user_id` (FK to `users.id`, nullable)
   - `user_role` (String)
   - `question_length` (Integer)
   - `retrieval_count` (Integer)
   - `retrieval_latency_ms` (Float)
   - `generation_latency_ms` (Float)
   - `total_latency_ms` (Float)
   - `outcome` (`answered`, `insufficient_evidence`, `error`, `unauthorized`)
   - `created_at` (Timestamp)

---

## 5. Security & RBAC Enforcement Matrix

| Resource / Action | Student | Faculty | Admin |
|---|---|---|---|
| View public / student documents | Yes | Yes | Yes |
| View faculty-only documents | **NO (Forbidden)** | Yes | Yes |
| View admin-only documents | **NO (Forbidden)** | **NO (Forbidden)** | Yes |
| Retrieval vector query | Matches <= `student` | Matches <= `faculty` | Matches all (`admin`, `faculty`, `student`) |
| Ingest new documents | **NO (403)** | **NO (403)** | Yes |
| Delete/Manage documents | **NO (403)** | **NO (403)** | Yes |
| Access conversation history | Own only | Own only | Own only (or audit mode) |
| Ask chat questions | Yes | Yes | Yes |

### Mandatory Retrieval-Time Access Enforcement
Access constraints are applied **directly inside the SQL/pgvector query**:
```sql
SELECT chunk_text, page_number, section_heading, (1 - (embedding <=> :query_vector)) AS similarity
FROM document_chunks
WHERE audience_role IN (:allowed_roles)
  AND (1 - (embedding <=> :query_vector)) >= :similarity_threshold
ORDER BY embedding <=> :query_vector ASC
LIMIT :top_k;
```
Restricted chunks **never reach the LLM prompt context**, eliminating any chance of context leakage or prompt bypass.

---

## 6. Gap Analysis & Missing Features

As this is a greenfield initialization for the backend repository:
1. **Application Core**: Needs FastAPI initialization, config via `pydantic-settings`, CORS middleware, structured logging, custom exception handlers.
2. **Database & Vector Layer**: Needs SQLAlchemy models, connection pool, pgvector integration, fallback/mock vector search adapter for isolated unit testing when PostgreSQL service is unavailable.
3. **Auth & RBAC**: Needs password hashing (Argon2 / Bcrypt), JWT token issuance/validation, security dependencies (`get_current_user`, `require_role`).
4. **Document Ingestion**: Needs file validation, PDF/DOCX/TXT extractors, recursive/semantic text chunker, batch embedding generator.
5. **Retrieval & RAG Pipeline**: Needs embedding service, pgvector similarity search, similarity threshold validator, prompt builder, LLM client with retry & fallback, and citation resolver.
6. **Persistence & Auditing**: Needs conversation storage, message logs, and privacy-preserving query audit logging.
7. **Test Suite**: Needs thorough unit tests (auth, chunking, retrieval, thresholding, RBAC, citations) and API tests.
8. **DevOps & Integration**: Needs `Dockerfile`, `docker-compose.yml` (backend + PostgreSQL + pgvector), `.env.example`, `docs/api-contract.md`, `docs/integration-checklist.md`.

---

## 7. Recommended Implementation Sequence

1. **Step 1**: Establish dependencies (`requirements.txt`, `pyproject.toml`) and environment configuration (`.env.example`).
2. **Step 2**: Create clean modular architecture in `app/`:
   - `app/core/` (settings, security, exceptions, logging)
   - `app/db/` (session, base, engine, pgvector setup)
   - `app/models/` (User, Document, DocumentChunk, Conversation, Message, QueryLog)
   - `app/schemas/` (Pydantic validation models for all contracts)
3. **Step 3**: Implement Authentication and Role-Based Access Control (`app/services/auth.py`, `app/api/dependencies.py`).
4. **Step 4**: Implement Ingestion Pipeline (`app/ingestion/`: extractors, chunkers, validator).
5. **Step 5**: Implement Embedding & Retrieval Engine (`app/embeddings/`, `app/retrieval/`: vector search with DB-level RBAC).
6. **Step 6**: Implement RAG Pipeline (`app/rag/`: prompt construction, LLM client, citation builder, insufficient-evidence gatekeeper).
7. **Step 7**: Implement API Routes (`app/api/routes/`: auth, chat, conversations, admin documents, health/ready).
8. **Step 8**: Implement Unit, API, RBAC, and Mocked RAG test suites (`tests/`).
9. **Step 9**: Execute test suite, fix any failures, and document results with exact output.
10. **Step 10**: Create Teammate Integration artifacts (`docs/api-contract.md`, `docs/integration-checklist.md`, Docker setup).
11. **Step 11**: Generate Final Engineering Report in `docs/` and root documentation.
