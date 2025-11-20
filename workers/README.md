<!-- Workers README: executor skeleton -->
# PHANTOM Worker

Run worker locally:
```powershell
pip install -r requirements.txt; $env:REDIS_URL="redis://localhost:6379/0"; $env:BACKEND_URL="http://localhost:8000"; python executor_worker.py
```

Notes:
- Uses Redis list `phantom:tasks`.
- TODO: Move to RQ/Celery with retries and metrics.
