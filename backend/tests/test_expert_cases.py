"""Expert backend tests covering edge cases expected by API contract."""
import os
import sys
import uuid
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app  # noqa: E402

client = TestClient(app)


def register(email: str, password: str = "Passw0rd!") -> str:
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_register_duplicate_email_returns_400():
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    register(email)
    r = client.post("/api/auth/register", json={"email": email, "password": "Passw0rd!"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Email already registered"


def test_login_invalid_password_401():
    email = f"badpwd_{uuid.uuid4().hex[:8]}@example.com"
    register(email, "CorrectP@ss1")
    r = client.post("/api/auth/login", json={"email": email, "password": "WrongP@ss1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


def test_status_nonexistent_task_404():
    token = register(f"status_{uuid.uuid4().hex[:8]}@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    bogus = uuid.uuid4().hex
    r = client.get(f"/api/status/{bogus}", headers=headers)
    assert r.status_code == 404


def test_worker_log_unknown_task_404():
    # Ensure expected worker token is set
    os.environ["WORKER_TOKEN"] = "devworkertoken"
    bogus = uuid.uuid4().hex
    r = client.post(
        "/api/worker/log",
        json={"task_uuid": bogus, "status": "done", "payload": {"note": "n/a"}},
        headers={"X-Worker-Token": "devworkertoken"},
    )
    assert r.status_code == 404
