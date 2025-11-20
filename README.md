<!-- README: Project overview and run instructions -->

# PHANTOM — Personal AI Assistant (MVP scaffold)

This repository contains a runnable MVP scaffold for PHANTOM (personal AI assistant).

Tech highlights (short justification):

- Frontend: Next.js + React + Tailwind CSS — server-side rendering and static page support for fast UX.
- Backend: FastAPI — lightweight, async-ready, and excellent DX for Python AI orchestration APIs.
- Workers: Python worker using Redis queue (simple blpop executor) — lightweight queue pattern for background tasks.
- Databases: PostgreSQL primary, Redis for queue/cache, optional Vector DB (Qdrant) stub for later.
- Containerization: Docker + Docker Compose — reproducible dev and prod stacks.
- Tests: Pytest for backend/workers; Jest + React Testing Library for frontend.

Purpose of this scaffold:

- Provide a minimal, production-minded monorepo with frontend, backend, workers, infra, tests, and CI.
- Include clear TODO markers where advanced AI integrations and features should be implemented.

Quick start (dev):

1. Copy `infra/.env.example` to `infra/.env` and adjust values.

2. Start with Docker Compose (build images):

```powershell
docker-compose -f infra/docker-compose.yml up --build
```

3. Backend API: http://localhost:8000/docs
4. Frontend: http://localhost:3000

Run tests:

Backend tests:

```powershell
cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; pytest -q
```

Frontend tests:

```powershell
cd frontend; npm ci; npm test -- --watchAll=false
```

Run worker (dev):

```powershell
cd workers; pip install -r requirements.txt; $env:REDIS_URL="redis://localhost:6379/0"; $env:BACKEND_URL="http://localhost:8000"; python executor_worker.py
```

Security & policy notes:

- Auth implemented (JWT access tokens). TODO: add refresh tokens, rate-limiting, RBAC, anomaly detection.
- Secrets are provided via `.env`; do not commit secrets to git.

6-month memory policy:

- By default, PHANTOM retains short-term runtime logs and task metadata only. Vector DB and long-term memory features are planned; when implemented they will include retention controls and deletion endpoints.

TODO (high level):

- TODO: Model routing, A2A flows, vector DB integration (Qdrant), wake-word STT, advanced plan generator, workflow DAG engine.

Auth usage (sample):

```bash
curl -X POST http://localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{"email":"user@example.com","password":"Pass123!"}'
TOKEN="$(curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"user@example.com","password":"Pass123!"}' | jq -r .access_token)"
curl -X POST http://localhost:8000/api/goal -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"title":"My Goal","description":"Desc"}'
```
