# CampusMind Backend

CampusMind is an AI-powered campus information assistant that answers questions using authorized campus documents. It provides grounded, hallucination-free responses with source citations, enforced through a three-tier Role-Based Access Control (RBAC) architecture: **Student**, **Faculty**, and **Administrator**.

---

## Person 2 — Backend Master Prompt

The complete specification, role responsibilities, architecture guidelines, and non-negotiable engineering rules for Person 2 (Backend Engineering + AI/RAG + Database + Security + Testing + Integration) are preserved verbatim in:

- [docs/README_PERSON2_MASTER_PROMPT.md](docs/README_PERSON2_MASTER_PROMPT.md)

---

## Key Architecture & Features

1. **FastAPI Modular Backend:** Clean layered structure separating API routing, domain services, schemas, and database models.
2. **PostgreSQL & pgvector Integration:** Relational database with vector similarity search using the cosine distance operator (`<=>`). Dual-dialect support allows testing with SQLite.
3. **Retrieval-Time Access Enforcement (Mandatory Rule):**
   - Access control constraints are applied **inside the database retrieval query before content reaches the LLM**.
   - Student queries never retrieve faculty or administrative documents.
   - Faculty queries never retrieve administrative documents.
   - Restricted evidence never enters the LLM prompt context.
4. **Insufficient-Evidence Gatekeeping:**
   - If vector search finds no authorized chunks meeting the relevance threshold (`SIMILARITY_THRESHOLD=0.30`), **the LLM generation is completely skipped**.
   - A standardized insufficient-information response is returned with zero fabricated citations.
5. **Grounded RAG & Citation Validation:**
   - LLM prompts treat retrieved documents as untrusted evidence, guarding against prompt injection.
   - Source citations reflect actual retrieved chunks (document title, ID, page number, section heading, similarity score).
6. **Authentication & Security:**
   - Argon2id salted password hashing.
   - Signed JWT tokens with strict claim validation, role claims, and expiration.
   - Cross-user conversation privacy: users cannot view or delete another user's conversation threads.
7. **Document Ingestion Pipeline:**
   - Multipart file validation, size limits, and path traversal sanitization.
   - Text extractors for PDF (`pypdf`), Word (`python-docx`), and plain text (`txt`).
   - Semantic sliding-window chunker with boundary detection and metadata preservation.
   - Batch vector embeddings and transactional database persistence.

---

## Default Seed Test Accounts

The database seed script (`python -m app.db.init_db`) provisions three testing accounts:

| Role | Username | Email | Password | Access Level |
|---|---|---|---|---|
| **Student** | `student1` | `student1@campus.edu` | `Password123!` | Public academic policies, syllabi, tuition deadlines |
| **Faculty** | `faculty1` | `faculty1@campus.edu` | `Password123!` | Student documents + faculty handbooks, tenure guidelines |
| **Administrator** | `admin1` | `admin1@campus.edu` | `AdminPassword123!` | Full system access: admin protocols + document upload/delete |

---

## Local Development Setup

### 1. Prerequisites
- Python 3.12+
- Git

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Initialize Database & Seed Sample Documents
```bash
python -m app.db.init_db
```

### 5. Start the FastAPI Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`
- Liveness Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/ready`

---

## Running the Automated Test Suite

Run the full pytest suite:
```bash
python -m pytest -v
```

**Verified Test Result:**
- **Total Tests:** 33
- **Passed:** 33 (100% Pass Rate)
- **Execution Time:** ~3.2 seconds

The test suite covers:
- Unit tests: configuration, Argon2id hashing, JWT validation, token tampering, and expiration.
- RBAC tests: role hierarchy, route permission checks, unauthorized access rejection.
- Ingestion tests: path traversal protection, file validation, text cleaning, chunking.
- Retrieval tests: cosine similarity mathematics, database-level RBAC filtering across student/faculty/admin.
- RAG tests: insufficient-evidence gatekeeper (skipping LLM call), prompt injection protection.
- API tests: login, current user, document upload/listing/deletion, chat query, conversation ownership isolation.
- End-to-end integration test: 16-step complete campus workflow.

---

## Docker Deployment (DevOps & Person 3)

Run the backend alongside PostgreSQL and pgvector using Docker Compose:
```bash
docker compose up -d --build
```
This starts:
- `campusmind-postgres`: PostgreSQL 16 with pgvector extension on port `5432`.
- `campusmind-backend`: FastAPI application on port `8000` with non-root security and container healthcheck.

---

## Documentation Index

- [Person 2 — Master Prompt](docs/README_PERSON2_MASTER_PROMPT.md)
- [Repository Audit & Architecture](docs/backend-audit.md)
- [Frontend API Contract (Person 1)](docs/api-contract.md)
- [Three-Person Integration Checklist (Person 1 & 3)](docs/integration-checklist.md)
- [Implementation & Verification Status](docs/backend-implementation-status.md)
