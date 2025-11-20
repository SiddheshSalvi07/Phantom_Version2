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
- `DATABASE_URL` — Postgres connection string
- `REDIS_URL` — Redis connection string

API docs: http://localhost:8000/docs
