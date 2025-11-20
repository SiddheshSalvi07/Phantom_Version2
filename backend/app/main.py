"""Backend FastAPI app and API endpoints for PHANTOM MVP with auth + persistence."""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from sqlalchemy.orm import Session
from . import schemas, worker_client, crud, auth
import os

app = FastAPI(title="PHANTOM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crud.ensure_db()


class RegisterPayload(BaseModel):
    email: str
    password: str

class LoginPayload(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
def register(payload: RegisterPayload, db: Session = Depends(crud.get_db)):
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, payload.email, payload.password)
    token = auth.create_access_token(user.id, user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/auth/login")
def login(payload: LoginPayload, db: Session = Depends(crud.get_db)):
    user = crud.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(user.id, user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/goal")
def create_goal(payload: schemas.GoalCreate, current_user=Depends(auth.get_current_user), db: Session = Depends(crud.get_db)):
    plan = [
        {"step": 1, "title": "Clarify goal", "notes": "Ask for clarification if needed."},
        {"step": 2, "title": "Draft plan", "notes": "Create a multi-step plan."},
        {"step": 3, "title": "Execute", "notes": "Run tasks via workers."},
    ]
    task = crud.create_task(db, current_user.id, payload.title, payload.description, plan)
    return {"task_uuid": task.task_uuid, "plan": plan}


@app.get("/api/status/{task_uuid}")
def get_status(task_uuid: str, current_user=Depends(auth.get_current_user), db: Session = Depends(crud.get_db)):
    task = crud.get_task_by_uuid(db, task_uuid)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="task not found")
    return {"task_uuid": task_uuid, "status": task.status, "approved": bool(task.approved)}


@app.post("/api/approve/{task_uuid}")
def approve_task(task_uuid: str, current_user=Depends(auth.get_current_user), db: Session = Depends(crud.get_db)):
    task = crud.get_task_by_uuid(db, task_uuid)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="task not found")
    task = crud.approve_task(db, task)
    return {"task_uuid": task.task_uuid, "approved": True}


@app.post("/api/execute/{task_uuid}")
def execute_task(task_uuid: str, current_user=Depends(auth.get_current_user), db: Session = Depends(crud.get_db)):
    task = crud.get_task_by_uuid(db, task_uuid)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="task not found")
    if not bool(task.approved):
        raise HTTPException(status_code=400, detail="task not approved")
    worker_client.enqueue_task({"task_uuid": task_uuid, "task": {"title": task.title}})
    crud.queue_task(db, task)
    return {"task_uuid": task_uuid, "status": "queued"}


class WorkerLog(BaseModel):
    task_uuid: str
    status: str
    payload: dict

@app.post("/api/worker/log")
def worker_log(entry: WorkerLog, x_worker_token: str = Header(None), db: Session = Depends(crud.get_db)):
    expected = os.getenv("WORKER_TOKEN", "devworkertoken")
    if x_worker_token != expected:
        raise HTTPException(status_code=401, detail="Invalid worker token")
    task = crud.get_task_by_uuid(db, entry.task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    created = crud.create_task_log(db, task, entry.status, entry.payload)
    return {"ok": True, "db_written": created is not None}
