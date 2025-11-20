"""Simple CRUD helpers for task logs. This is intentionally minimal for the MVP."""
from .models import SessionLocal, TaskLog, init_db
import json

def ensure_db():
    if SessionLocal is None:
        init_db()

def create_task_log(task_id: str, status: str, payload: dict):
    ensure_db()
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        entry = TaskLog(task_id=task_id, status=status, payload=json.dumps(payload))
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    finally:
        db.close()
