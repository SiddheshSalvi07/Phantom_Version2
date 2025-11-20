"""Comprehensive backend tests: auth, task lifecycle, security constraints."""
import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

client = TestClient(app)

TEST_EMAIL = "user@example.com"
TEST_PASSWORD = "StrongPass123!"


def register_and_login():
    r = client.post("/api/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return token


def test_goal_requires_auth():
    r = client.post("/api/goal", json={"title": "NoAuth", "description": "Should fail"})
    assert r.status_code == 401


def test_register_login_and_lifecycle():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Create goal
    r_goal = client.post("/api/goal", json={"title": "Test Goal", "description": "Do X"}, headers=headers)
    assert r_goal.status_code == 200
    task_uuid = r_goal.json()["task_uuid"]
    assert task_uuid

    # Status should be created
    r_status = client.get(f"/api/status/{task_uuid}", headers=headers)
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "created"

    # Execute should fail before approval
    r_exec_fail = client.post(f"/api/execute/{task_uuid}", headers=headers)
    assert r_exec_fail.status_code == 400

    # Approve
    r_app = client.post(f"/api/approve/{task_uuid}", headers=headers)
    assert r_app.status_code == 200
    assert r_app.json()["approved"] is True

    # Execute now
    r_exec = client.post(f"/api/execute/{task_uuid}", headers=headers)
    assert r_exec.status_code == 200
    assert r_exec.json()["status"] == "queued"

    # Worker log with correct token
    worker_token = os.getenv("WORKER_TOKEN", "devworkertoken")
    r_log = client.post("/api/worker/log", json={"task_uuid": task_uuid, "status": "done", "payload": {"note": "ok"}}, headers={"X-Worker-Token": worker_token})
    assert r_log.status_code == 200
    assert r_log.json()["ok"] is True

    # Worker log with wrong token
    r_log_bad = client.post("/api/worker/log", json={"task_uuid": task_uuid, "status": "done", "payload": {}}, headers={"X-Worker-Token": "WRONG"})
    assert r_log_bad.status_code == 401


def test_second_user_cannot_access_first_task():
    # First user creates task
    token1 = register_and_login()
    h1 = {"Authorization": f"Bearer {token1}"}
    r_goal = client.post("/api/goal", json={"title": "User1 Task"}, headers=h1)
    task_uuid = r_goal.json()["task_uuid"]

    # Second user registers
    r2 = client.post("/api/auth/register", json={"email": "user2@example.com", "password": TEST_PASSWORD})
    token2 = r2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {token2}"}

    # Second user status access should 404
    r_status = client.get(f"/api/status/{task_uuid}", headers=h2)
    assert r_status.status_code == 404
"""Comprehensive tests for auth and task lifecycle with security checks."""
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

client = TestClient(app)

EMAIL = "user@example.com"
PASSWORD = "secret123"

def register_and_login():
    r = client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return token

def login():
    r = client.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_register_login_and_goal_flow():
    token = register_and_login()
    # Create goal
    goal_payload = {"user_id": "ignored-now", "title": "My Goal", "description": "Desc"}
    r_goal = client.post("/api/goal", json=goal_payload, headers={"Authorization": f"Bearer {token}"})
    assert r_goal.status_code == 200
    task_uuid = r_goal.json()["task_uuid"]
    # Status requires auth
    r_status = client.get(f"/api/status/{task_uuid}", headers={"Authorization": f"Bearer {token}"})
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "created"
    # Approve
    r_app = client.post(f"/api/approve/{task_uuid}", headers={"Authorization": f"Bearer {token}"})
    assert r_app.status_code == 200
    # Execute
    r_exec = client.post(f"/api/execute/{task_uuid}", headers={"Authorization": f"Bearer {token}"})
    assert r_exec.status_code == 200
    assert r_exec.json()["status"] == "queued"

def test_unauthorized_access_blocked():
    # Goal without token should fail
    r = client.post("/api/goal", json={"user_id": "x", "title": "T"})
    assert r.status_code in (401, 403)

def test_worker_log_requires_token():
    token = login() if client.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD}).status_code == 200 else register_and_login()
    goal_payload = {"user_id": "ignored", "title": "WorkerTest", "description": "D"}
    r_goal = client.post("/api/goal", json=goal_payload, headers={"Authorization": f"Bearer {token}"})
    task_uuid = r_goal.json()["task_uuid"]
    client.post(f"/api/approve/{task_uuid}", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/execute/{task_uuid}", headers={"Authorization": f"Bearer {token}"})
    # Missing worker token
    r_log_fail = client.post("/api/worker/log", json={"task_uuid": task_uuid, "status": "done", "payload": {}})
    assert r_log_fail.status_code == 401
    # Correct token
    os.environ["WORKER_TOKEN"] = "devworkertoken"
    r_log_ok = client.post("/api/worker/log", json={"task_uuid": task_uuid, "status": "done", "payload": {"note": "ok"}}, headers={"X-Worker-Token": "devworkertoken"})
    assert r_log_ok.status_code == 200
    assert r_log_ok.json()["ok"] is True
