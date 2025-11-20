"""Unit tests for backend API endpoints."""
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def test_post_goal_creates_task():
    payload = {"user_id": "u1", "title": "Test Goal", "description": "Do X"}
    r = client.post("/api/goal", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "task_id" in data
    assert "plan" in data


def test_status_endpoint():
    payload = {"user_id": "u2", "title": "Stat Goal"}
    r = client.post("/api/goal", json=payload)
    tid = r.json()["task_id"]
    r2 = client.get(f"/api/status/{tid}")
    assert r2.status_code == 200
    assert r2.json()["status"] == "created"


def test_enqueue_task_requires_approval_and_queues():
    payload = {"user_id": "u3", "title": "Queue Goal"}
    r = client.post("/api/goal", json=payload)
    tid = r.json()["task_id"]
    # executing without approval should fail
    r_exec = client.post(f"/api/execute/{tid}")
    assert r_exec.status_code == 400
    # approve then execute
    r_app = client.post(f"/api/approve/{tid}")
    assert r_app.status_code == 200
    r_exec2 = client.post(f"/api/execute/{tid}")
    assert r_exec2.status_code == 200
    assert r_exec2.json()["status"] == "queued"
