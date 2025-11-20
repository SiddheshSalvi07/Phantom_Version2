"""CRUD helpers for users, tasks, and logs."""
from .models import SessionLocal, TaskLog, Task, User, init_db
from uuid import uuid4
import json
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def ensure_db():
    if SessionLocal is None:
        init_db()

def get_db():
    ensure_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_user(db, email: str, password: str):
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_task(db, owner_id: int, title: str, description: str | None, plan: list):
    task = Task(task_uuid=str(uuid4()), owner_id=owner_id, title=title, description=description, plan=json.dumps(plan))
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task_by_uuid(db, task_uuid: str):
    return db.query(Task).filter(Task.task_uuid == task_uuid).first()

def approve_task(db, task: Task):
    task.approved = 1
    task.status = "approved"
    db.commit()
    db.refresh(task)
    return task

def queue_task(db, task: Task):
    task.status = "queued"
    db.commit()
    db.refresh(task)
    return task

def create_task_log(db, task: Task, status: str, payload: dict):
    entry = TaskLog(task_id=task.id, status=status, payload=json.dumps(payload))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
