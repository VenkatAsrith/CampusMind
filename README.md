# CampusMind — AI-Powered Campus Information Platform

**CampusMind** is a production-oriented, cloud-ready campus AI assistant built with FastAPI, PostgreSQL + pgvector, Anthropic Claude 3.5 Sonnet, and a ChatGPT-style React/TypeScript frontend.

It provides hallucination-free, grounded responses with verifiable source citations, enforced through a strict three-tier Role-Based Access Control (RBAC) model: **Student**, **Faculty**, and **Administrator**.

---

## 1. Architecture & Repository Structure

CampusMind is structured as a clean full-stack workspace:

```
CampusMind/
├── backend/                   # Python FastAPI Backend & AI/RAG Pipeline
│   ├── app/
│   │   ├── api/routes/        # Auth, Chat, Conversations, Admin Documents, Health
│   │   ├── core/              # Config (Anthropic, DB, JWT), Security, Exceptions
│   │   ├── db/                # SQLAlchemy session, engine, seed data (init_db.py)
│   │   ├── models/            # User, Document, DocumentChunk (pgvector), Conversation
│   │   ├── schemas/           # Pydantic v2 schemas
│   │   ├── ingestion/         # PDF, DOCX, TXT extractors and sliding-window chunker
│   │   ├── embeddings/        # Sentence-Transformers service (all-MiniLM-L6-v2)
│   │   ├── retrieval/         # DB-level RBAC vector retrieval engine
│   │   └── rag/               # Anthropic Messages API client, prompt builder, citations
│   ├── tests/                 # 41 Pytest unit, API, RBAC, and security tests
│   ├── requirements.txt       # Locked backend dependencies
│   └── Dockerfile             # Multi-stage non-root container
│
├── frontend/                  # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/        # Sidebar, ChatArea, AdminKnowledgeStudio, Modals
│   │   ├── lib/api-client.ts  # Typed API client with token management & error handling
│   │   └── types/             # TypeScript data contracts
│   ├── package.json           # Frontend dependencies (Lucide, ReactMarkdown, Vitest)
│   └── Dockerfile             # Multi-stage Nginx static container
│
├── docs/                      # Architectural & Operational Documentation
│   ├── IMPLEMENTATION_ROADMAP.md # Phase Zero repository audit & delivery roadmap
│   ├── api-contract.md        # Complete frontend-backend REST contract
│   ├── SECURITY_AUDIT.md      # OWASP & RBAC security review
│   ├── DEPLOYMENT.md          # Cloud deployment guide (AWS, Render, Vercel)
│   └── OPERATIONS.md          # Monitoring, health checks, troubleshooting
│
├── docker-compose.yml         # Multi-service composition (Postgres/pgvector, Backend, Frontend)
└── .github/workflows/ci.yml   # GitHub Actions automated test & build workflow
```

---

## 2. Key Capabilities & Engineering Highlights

1. **ChatGPT-Inspired User Experience**:
   - Clean, distraction-free conversational layout with collapsible sidebar.
   - Date-grouped conversation history (Today, Yesterday, Previous 7 Days).
   - Conversation rename (`PATCH /api/conversations/{id}`) and delete actions with confirmation.
   - Markdown rendering for headings, lists, tables, and code blocks.
   - Interactive source citation cards with document title, section, page number, and similarity score.
   - Dark/Light mode support.

2. **Server-Side Identity-Aware @ Mention Workflow**:
   - Typing `@` opens an accessible autocomplete menu (`@student`, `@principal`, `@help`).
   - **Student Lookup (`@23SS1A0535`)**: Strictly verifies the authenticated student's ownership. Students can **never** view another student's personal record (horizontal privilege escalation is blocked with `403 Forbidden` and logged).
   - **Restricted Access (`@principal`)**: Prompts for dedicated institutional credentials and verifies the `admin` role server-side.

3. **Admin Knowledge Studio**:
   - Real-time operational dashboard with document counts, chunk metrics, and ingestion statuses.
   - Drag-and-drop file uploader for PDF, DOCX, and TXT with audience role selection (`student`, `faculty`, `admin`).
   - Search, filter by clearance, inspect SHA-256 metadata, and cascade deletion.

4. **Retrieval-Time Access Control & Anthropic Claude Integration**:
   - Access constraints are applied **inside the database query before content reaches the LLM**.
   - If evidence fails the relevance threshold (`SIMILARITY_THRESHOLD >= 0.30`), LLM generation is skipped to prevent hallucinations.
   - Grounded factual synthesis powered by the official **Anthropic Claude Messages API** (`claude-3-5-sonnet-20241022`).

---

## 3. Pre-Seeded Demonstration Accounts

The database seed routine (`backend/app/db/init_db.py`) automatically provisions:

| Role | Username / Handle | Password | Clearance & Purpose |
|---|---|---|---|
| **Student** | `23SS1A0535` | `Password123!` | Roll-number student identity; personal attendance & coursework |
| **Student (Alt)** | `student1` | `Password123!` | General student clearance; campus policies & calendar |
| **Faculty** | `faculty1` | `Password123!` | Faculty clearance; sabbatical rules & grading curves |
| **Administrator** | `admin1` | `AdminPassword123!` | Knowledge Studio management, document ingestion & deletion |
| **Principal** | `principal` | `Principal123!` | Executive administrative clearance for `@principal` elevation |

---

## 4. Local Development Setup

### 4.1 Running the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/health`

### 4.2 Running the Frontend

```bash
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
- Application UI: `http://localhost:5173`

---

## 5. Automated Testing

### Backend Test Suite (Pytest)
```bash
cd backend
.venv\Scripts\python -m pytest -v tests
```
*Current Suite: 41 tests passing (Auth, RAG, RBAC, Ingestion, Mention Security, Conversations, Health)*

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
*Current Suite: 3 unit tests passing (API client, token persistence, mention filtering)*

### Production Build
```bash
cd frontend
npm run build
```

---

## 6. Docker Deployment

Launch PostgreSQL with pgvector, the FastAPI backend, and the React frontend in Docker:

```bash
# In the repository root:
cp .env.example .env
# Add your ANTHROPIC_API_KEY into .env

docker compose up --build -d
```
Access the application at :: Link will be updated soon !!
.
