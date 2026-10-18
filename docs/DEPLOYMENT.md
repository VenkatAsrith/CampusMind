# CampusMind Cloud Deployment Guide

This guide details the procedure for deploying CampusMind to production cloud environments with a secure, private PostgreSQL + pgvector database, a Python FastAPI backend container, and a static React frontend.

---

## 1. Architecture Overview

```
                      ┌───────────────────────┐
                      │    Internet Users     │
                      └───────────┬───────────┘
                                  │ HTTPS
                   ┌──────────────┴──────────────┐
                   │   Cloud CDN / Reverse Proxy │
                   └──────┬───────────────┬──────┘
                          │               │
            Static Assets │               │ /api/*
                          ▼               ▼
             ┌─────────────────┐   ┌─────────────────────────┐
             │ Frontend (React)│   │ Backend (FastAPI / Py)  │
             │ Vercel / Nginx  │   │ Container (Render / ECS)│
             └─────────────────┘   └───────────┬─────────────┘
                                               │
                                 Private VPC   │
                                               ▼
                                   ┌─────────────────────────┐
                                   │ Managed PostgreSQL 16   │
                                   │ with pgvector extension │
                                   └─────────────────────────┘
```

---

## 2. Environment Variables Configuration

Set these variables in your hosting provider's Secret Manager (never commit to source control):

| Variable | Target | Purpose / Value |
|---|---|---|
| `ENVIRONMENT` | Backend | `production` |
| `DATABASE_URL` | Backend | `postgresql+psycopg2://user:password@host:5432/campusmind_db` |
| `JWT_SECRET_KEY` | Backend | High-entropy 64-character hex key (`openssl rand -hex 32`) |
| `LLM_PROVIDER` | Backend | `anthropic` |
| `ANTHROPIC_API_KEY` | Backend | `sk-ant-api03-...` (Server-side only) |
| `ANTHROPIC_MODEL` | Backend | `claude-3-5-sonnet-20241022` |
| `ALLOWED_CORS_ORIGINS` | Backend | `https://your-frontend-domain.com` |
| `VITE_API_BASE_URL` | Frontend | `https://your-backend-api.com/api` (or `/api` if using reverse proxy) |

---

## 3. Local & Staging Deployment (Docker Compose)

To run the complete platform locally or on a single staging virtual machine:

```bash
# 1. Clone repository
git clone https://github.com/RajaRajeshwari2609/campusMind.git
cd campusMind

# 2. Configure environment
cp .env.example .env
# Edit .env and insert your ANTHROPIC_API_KEY

# 3. Build and launch all services
docker compose up --build -d

# 4. Verify health
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/ready

# 5. Access Frontend
# Open your browser at http://localhost:3000
```

---

## 4. Production Cloud Deployment Steps

### Step 1: Provision Database with pgvector
1. Provision a PostgreSQL 16 instance on AWS RDS, Supabase, Neon, or Railway.
2. Enable the pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Step 2: Deploy Backend Container
1. Build and push the backend container to your container registry:
   ```bash
   docker build -t campusmind-backend:latest ./backend
   ```
2. Deploy to a container service (e.g., Render, Fly.io, AWS ECS Fargate, or Google Cloud Run).
3. Set all required environment variables in the provider dashboard.
4. Verify the liveness probe `/health` and readiness probe `/ready`.

### Step 3: Deploy Frontend Static Client
1. Deploy `./frontend` to Vercel, Netlify, or AWS CloudFront.
2. Set the build command to `npm run build` and output directory to `dist`.
3. Set `VITE_API_BASE_URL` to your live backend API URL.

---

## 5. Backup & Recovery

- **Database Backups**: Enable automated daily snapshots on the managed PostgreSQL database with 14-day retention.
- **Rollback**: In case of deployment issues, revert the container image tag to the previous stable release.
