"""Backend FastAPI app and API endpoints for PHANTOM MVP."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from . import schemas, worker_client
from . import crud

app = FastAPI(title="PHANTOM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store for MVP. TODO: persist in Postgres and add ownership.
TASK_STORE = {}


@app.post("/api/goal")
def create_goal(payload: schemas.GoalCreate):
    """Create a new goal/task and return initial mocked plan."""
    task_id = str(uuid4())
    # Mocked plan - placeholder for planner integration
    plan = [
        {"step": 1, "title": "Clarify goal", "notes": "Ask for clarification if needed."},
        {"step": 2, "title": "Draft plan", "notes": "Create a multi-step plan."},
        {"step": 3, "title": "Execute", "notes": "Run tasks via workers."},
    ]
    TASK_STORE[task_id] = {
        "user_id": payload.user_id,
        "title": payload.title,
        "description": payload.description,
        "status": "created",
        "plan": plan,
        "approved": False,
    }
    return {"task_id": task_id, "plan": plan}


@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=404, detail="task not found")
    data = TASK_STORE[task_id]
    return {"task_id": task_id, "status": data.get("status"), "approved": data.get("approved")}


@app.post("/api/approve/{task_id}")
def approve_task(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=404, detail="task not found")
    TASK_STORE[task_id]["approved"] = True
    TASK_STORE[task_id]["status"] = "approved"
    return {"task_id": task_id, "approved": True}


@app.post("/api/execute/{task_id}")
def execute_task(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=404, detail="task not found")
    task = TASK_STORE[task_id]
    if not task.get("approved"):
        raise HTTPException(status_code=400, detail="task not approved")
    # Enqueue the task for workers
    worker_client.enqueue_task({"task_id": task_id, "task": task})
    TASK_STORE[task_id]["status"] = "queued"
    return {"task_id": task_id, "status": "queued"}


class WorkerLog(BaseModel):
    task_id: str
    status: str
    payload: dict


@app.post("/api/worker/log")
def worker_log(entry: WorkerLog):
    """Endpoint for workers to submit execution logs. Persisted if DB is configured.

    TODO: secure this endpoint and add auth between workers and backend.
    """
    # Best-effort persistence
    created = crud.create_task_log(entry.task_id, entry.status, entry.payload)
    return {"ok": True, "db_written": created is not None}
