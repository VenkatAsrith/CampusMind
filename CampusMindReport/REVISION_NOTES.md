# CampusMind Stage-I Report: Revision Notes

Revised report: `CampusMind_Project_Report_Stage1.docx` and `CampusMind_Project_Report_Stage1_revised.pdf`. The PDF has 127 pages, clickable Contents, List of Figures and List of Tables, cross-references and citations, plus a bookmark outline.
Diagram sources: `uml/` (PlantUML and matplotlib). Rendered diagrams: `uml_png/`. Interface screenshots: `screenshots/`.
Revision date: 19 October 2026.

## 1. Revision summary

| Area | Change |
|---|---|
| Front matter | Title page and certificate follow the VeriChain Stage-I format. The declaration uses the VeriChain wording with team names and roll numbers in bold; academic year 2026 - 2027, September 2026. The Abstract is rewritten for Claude, RAG and the @ mention workflow. Five abbreviations are added. |
| Navigation | Contents uses Word TC fields (`TOC \o "2-3" \h \z \u \f`). The PDF is post-processed to add hyperref-style links: 169 Contents entries, 23 figures, 35 tables, 223 in-text references. It also gets a bookmark outline and page labels (Title / roman / arabic). |
| Appearance | Every chapter opens with a "Chapter n" label and a large title. All blue headings, shading and theme colours are replaced with black and grey. There are no watermarks. |
| Chapters 1-5 | Claims match the repository: FastAPI on Python 3.12, React 19 with Vite and Tailwind 4, PostgreSQL 16 with pgvector, all-MiniLM-L6-v2 (384-d), Argon2id, JWT HS256. FR-01 to FR-20 and NFR-01 to NFR-13 are rewritten. |
| Chapter 6 (UML) | Monochrome UML 2.x diagrams: use case, class, sequence, query activity, component and deployment, plus two new ones: 6.7 ingestion activity and 6.8 authentication / @ mention activity. |
| Chapter 7 | Equations 7.1-7.3 are native Word equations. The retrieval SQL, threshold gate and system prompt match the code. |
| Chapter 8 | Retitled "Implementation and Deployment". New: 8.9 Implementation Status (Table 8.2), 8.10 Containerisation, CI/CD and Deployment, 8.11 Team Responsibilities. |
| Chapter 9 | Tables 9.1-9.6 and Listing B.1 describe the schema as implemented (integer keys, UUID conversations, `citations_json`, `query_logs`). The ER diagram is redrawn. 9.3 covers planned normalisation. |
| Chapter 10 | RBAC matrix (Table 10.1). 10.9 Rate Limiting is marked planned. 10.13 Secure @ Mention Workflow (Table 10.3). |
| Chapters 11-12 | TC-01 to TC-32 are mapped to the real tests. 11.4 reports the actual test run. Evaluation metrics (12.1-12.6) are defined but not presented as measured. |
| Chapter 13 | Real screenshots from a local test instance replace the five placeholder figures. They are labelled as a mocked-services run. 13.6 Verified Outcomes is new. |
| Appendices / references | Appendix F (configuration) and Appendix G (diagram sources) are new. References [47] Anthropic docs, [48] RFC 9106 and [49] GitHub Actions docs are added; [39] is now pypdf. |

## 2. Team responsibilities (Table 8.4)

| Member | Roll no. | Area |
|---|---|---|
| Harika Bolli | 23SS1A0511 | Frontend and UX |
| Rajarajeshwari Nimmanagoti | 23SS1A0546 | Backend, AI/RAG and database |
| Venkat Asrith Konam | 23SS1A0535 | DevOps, QA and deployment |

## 3. Traceability

| Requirement | Report sections / diagrams | Code |
|---|---|---|
| Login, JWT, roles | 6.8, 10.2-10.4, Table 10.1, Fig 13.1 | `app/api/routes/auth.py`, `app/core/security.py` |
| Document ingestion | 5.2, 6.7, 7.2, Fig 5.2, Fig 13.5 | `app/api/routes/documents.py`, `app/ingestion/service.py`, `app/embeddings/service.py` |
| Role-filtered retrieval | 5.3, 6.3, 6.4, 7.3, Listing 7.2 | `app/retrieval/vector_engine.py` |
| Grounded answer with citations | 7.4-7.6, Fig 13.2, Fig 13.3 | `app/rag/orchestrator.py`, `app/rag/prompt.py`, `app/rag/llm.py`, `app/rag/citation.py` |
| Insufficient-evidence refusal | 6.4, 7.5, Fig 13.4 | `app/rag/orchestrator.py` |
| Conversation history and ownership | 9.1, 10.6 | `app/api/routes/conversations.py` |
| @ mention student record | 6.8, 10.13, Table 10.3 | `app/api/routes/chat.py` (`/mentions`), `app/api/routes/auth.py` (`/student/{id}`) |
| Containers and CI | 8.10, Fig 6.6 | `docker-compose.yml`, Dockerfiles, `.github/workflows/ci.yml` |

## 4. Verification done (19 October 2026)

- Backend tests: 41 passed (Python 3.12.2, SQLite, mocked embeddings and language model).
- Frontend tests: 3 passed (Vitest, Node 22.16.0).
- Screenshots: taken from an isolated local instance (SQLite, seeded demo data, mocked AI services). The answer text in Fig 13.2 / 13.3 is the mock template.
- PDF: every Contents, figure and table entry resolves to the correct page; the pages were checked visually.

## 5. Verification checklist (still to do)

- [ ] Add `sentence-transformers` to `requirements.txt`. Without it the service silently falls back to hash-based mock embeddings.
- [ ] Replace `:query_vector::vector` with `CAST(:query_vector AS vector)` and create the HNSW index. Without the fix, native pgvector search fails and ranking falls back to Python.
- [ ] Set `ANTHROPIC_MODEL` to a current model (the default `claude-3-5-sonnet-20241022` is retired) and remove the `temperature` argument, which current models reject.
- [ ] Remove the seeded demo accounts (known passwords, including `principal`) and the default secrets in `docker-compose.yml` before any shared deployment.
- [ ] Remove the login page's quick-select test-account buttons, and drive the "Claude 3.5 Sonnet" header badge from configuration.
- [ ] Check why the `ALLOWED_CORS_ORIGINS` environment variable did not override `.env` in testing.
- [ ] Test the `conversation_id` ownership edge case on `/api/chat/query` (a query sent with someone else's conversation id).
- [ ] Run the full stack on PostgreSQL 16 + pgvector with real embeddings.
- [ ] Run against a live Claude model and record answer quality and latency (Chapter 12 metrics).
- [ ] Test PDF and DOCX extraction with real institutional documents.
- [ ] Run the GitHub Actions workflow and record the result.
- [ ] Implement rate limiting (Section 10.9).
- [ ] Replace the demonstration student record with the real data source.

## 6. Editing notes

- If you press F9 / "Update field" on the Contents in Word, Word removes the bold chapter lines and no-leader formatting. Updating page numbers only is safe.
- Word's own PDF export on this machine does not keep links. The clickable PDF was produced by post-processing, so export from Word again only if you don't need the links.
