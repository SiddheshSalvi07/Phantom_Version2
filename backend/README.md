<!-- Backend README: API and tests -->

# PHANTOM Backend

Run locally:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload
```

Run tests:

```powershell
pytest -q
```

Environment:

- `DATABASE_URL` — Postgres connection string (fallback sqlite if absent)
- `REDIS_URL` — Redis connection string
- `JWT_SECRET` / `JWT_ALG` — JWT token signing configuration
- `WORKER_TOKEN` — shared secret for worker log ingestion

API docs: http://localhost:8000/docs

Auth usage example:

```bash
curl -X POST http://localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{"email":"user@example.com","password":"Pass123!"}'
curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"user@example.com","password":"Pass123!"}'
```
