# CampusMind — Master Implementation Roadmap & Repository Audit

**Platform:** CampusMind — AI-Powered Campus Assistant with pgvector, RBAC, and ChatGPT-Style Interface  
**Date:** October 2026  
**Auditor:** Principal Software Architect & Full-Stack Engineer  
**Workspace Structure:** Mono-repo with `backend/` (FastAPI + pgvector + Anthropic) and `frontend/` (React + TypeScript + Vite + Tailwind CSS)

---

## 1. Executive Summary & Audit Baseline

A comprehensive Phase Zero repository audit was conducted across all files, database models, API routes, security controls, and automated tests.

### 1.1 Baseline Test Suite Execution
- **Environment**: Python 3.12.2 on Windows, isolated virtual environment `backend/.venv`
- **Command Executed**: `pytest -v tests`
- **Result**: **33 Passed, 0 Failed** (Execution time: 2.01s)
- **Summary**: All 33 core backend unit, API, RBAC, and ingestion tests passed successfully before modification.

---

## 2. Detailed Findings & Gap Analysis

| Subsystem | Existing State | Identified Gap / Requirement | Priority |
|---|---|---|---|
| **Directory Organization** | Cloned files originally in root | Separated cleanly into `backend/` (FastAPI) and `frontend/` (Vite/React) as directed | Complete |
| **LLM Provider** | OpenAI Chat Completions in `app/rag/llm.py` | Need official **Anthropic Messages API** adapter with configurable Claude models (`claude-3-5-sonnet-20241022`), fallback retries, and bounded tokens | High |
| **@ Mention Workflow** | No mention endpoints | Implement backend verification for `@<roll_number>` ownership enforcement (prevent horizontal privilege escalation) and `@principal` elevated credential authentication | High |
| **Conversation Management** | List, Get, Delete implemented | Need `PATCH /api/conversations/{conversation_id}` for conversation rename backed by strict ownership checks | High |
| **Admin Knowledge Studio** | Upload, List, Get, Delete implemented | Need `GET /api/admin/stats` summary endpoint for knowledge metrics (total documents, completed, failed, chunks) | Medium |
| **Pydantic Schemas** | Pydantic V2 deprecation warnings (`example` instead of `json_schema_extra`) | Clean up deprecation warnings in `app/schemas/` | Low |
| **Frontend Client** | Previously non-existent | Build complete React 19 + TypeScript + Vite + Tailwind CSS application with ChatGPT-style conversation UI, Admin Knowledge Studio, and Mention Autocomplete | High |
| **DevOps & Containers** | Root Dockerfile assumed single folder | Multi-service `docker-compose.yml` supporting `backend`, `frontend`, and `postgres` with pgvector | Medium |
| **CI/CD** | No GitHub Actions workflow | Create GitHub Actions workflow testing backend and building frontend on push/PR | Medium |

---

## 3. Phased Implementation Plan

### Phase A: Audit & Baseline (Completed)
- Cloned and organized repository into `backend/` and `frontend/`.
- Configured `.venv` and verified all 33 baseline tests pass.
- Scaffolded Vite React + TypeScript frontend with Tailwind CSS v4 and Lucide icons.

### Phase B: Backend Stabilization & Anthropic Claude Adapter
- Extend `app/core/config.py` with Anthropic configuration (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `LLM_PROVIDER`).
- Implement Anthropic Messages API client in `app/rag/llm.py` with structured logging, retries, and test-safe mock mode.
- Add `PATCH /api/conversations/{conversation_id}` endpoint for conversation renaming with ownership verification.
- Add `GET /api/auth/student/{identifier}` for student record lookup enforcing that the authenticated student can only access their own records.
- Add `GET /api/chat/mentions` for mention suggestions without leaking unauthorized data.
- Add `GET /api/admin/stats` for real-time document counts and status aggregation.
- Seed demo users (`23SS1A0535` student, `faculty1`, `admin1`, `principal`) in `app/db/init_db.py`.

### Phase C: Frontend Foundation & API Client
- Configure typed API client in `frontend/src/lib/api-client.ts` with centralized error handling (401, 403, 404, 422, 500).
- Build accessible theme system, CSS variables, and layout container.
- Implement responsive layout with collapsible conversation sidebar.

### Phase D: ChatGPT-Style Conversational Experience
- Build conversation navigation (Today, Yesterday, Previous 7 Days).
- Implement interactive chat area with markdown rendering, tables, and source citation cards.
- Add suggestion chips for first-use onboarding.
- Support multiline input (Enter to send, Shift+Enter for newline).

### Phase E: Admin Knowledge Studio
- Upload documents (PDF, DOCX, TXT) with audience clearance selection (`student`, `faculty`, `admin`).
- Real-time ingestion metrics, document listing, filtering, and deletion with cascading chunk removal.

### Phase F: Identity-Aware @ Mention Workflow
- Accessible `@` autocomplete menu in message composer (`@student`, `@principal`, `@help`).
- Server-verified student roll number lookup and principal elevation dialog.

### Phase G: Automated Testing & Security Hardening
- Add tests for Anthropic adapter, conversation rename, mention authorization, and cross-student denial.
- Verify frontend production build and type checking.

### Phase H: Containerization, Hygiene, and Deployment
- Update `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`.
- Verify `.gitignore` and `.dockerignore`.
- Author `docs/SECURITY_AUDIT.md`, `docs/DEPLOYMENT.md`, `docs/OPERATIONS.md`.

---

## 4. Acceptance Criteria
1. Full RAG pipeline executes: document ingestion -> vector storage -> RBAC retrieval -> Claude/mock generation -> citations.
2. Students can never access faculty or admin documents or another student's roll number records.
3. @principal mention prompts for elevated credentials and verifies admin role server-side.
4. Conversations persist across browser reloads and strictly belong to the authenticated user.
5. All automated unit and API tests pass.
