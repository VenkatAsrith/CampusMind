# CampusMind Operations & Monitoring Manual

**Scope:** Operational runbook, health inspection, diagnostic logging, and incident troubleshooting.

---

## 1. Health & Readiness Monitoring

CampusMind exposes two unauthenticated operational probes:

### 1.1 Liveness Probe
`GET /health`
- **Purpose**: Verifies that the FastAPI process is responsive.
- **Expected Status**: `200 OK`
- **Response**:
  ```json
  {
    "status": "ok",
    "app_name": "CampusMind Backend",
    "environment": "production",
    "version": "1.0.0"
  }
  ```

### 1.2 Readiness Probe
`GET /ready`
- **Purpose**: Verifies database connectivity, pgvector extension state, and embedding dimensions.
- **Expected Status**: `200 OK`
- **Response**:
  ```json
  {
    "status": "ready",
    "database": "connected",
    "vector_support": true,
    "embedding_dimension": 384
  }
  ```

---

## 2. Structured Operational Logging

Application logs are emitted in JSON / standardized format to standard output. Log fields include:
- `timestamp`: UTC ISO-8601 timestamp
- `level`: `INFO`, `WARNING`, `ERROR`
- `logger`: `campusmind`
- `request_id`: Unique UUID assigned to the query
- `user_role`: Role of the querying user (`student`, `faculty`, `admin`)
- `retrieval_count`: Number of authorized chunks meeting relevance threshold
- `total_latency_ms`: End-to-end request latency

Sensitive student records, passwords, and bearer tokens are **never** logged.

---

## 3. Incident Troubleshooting Guide

### Issue 1: Insufficient Evidence Responses on Known Policies
- **Symptom**: User receives "I do not have sufficient information in the authorized campus documents..."
- **Diagnosis**:
  1. Verify the document was uploaded in Admin Knowledge Studio and holds status `completed`.
  2. Check the document's `audience_role`. If the document was ingested as `faculty` or `admin`, a student user cannot retrieve it.
  3. Inspect `SIMILARITY_THRESHOLD`. Default is `0.30`. If set too high (e.g. `0.70`), semantic variations in queries may be filtered out.

### Issue 2: Anthropic API Rate Limiting or Provider Unavailable
- **Symptom**: HTTP 500 error with message `LLM generation failed`.
- **Diagnosis**:
  1. Inspect backend container logs for `Anthropic API Error`.
  2. Verify that `ANTHROPIC_API_KEY` is active and holds sufficient credits.
  3. The client automatically executes bounded exponential backoff retries (up to 3 attempts).

### Issue 3: Ingestion Job Fails
- **Symptom**: Document processing status shows `failed` in Knowledge Studio.
- **Diagnosis**:
  1. Click the "Inspect Metadata" button on the document row in Knowledge Studio to read `error_message`.
  2. Ensure the uploaded file is not password-protected or corrupt.
