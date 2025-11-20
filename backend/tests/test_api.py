"""Adjusted tests to use auth flow and new response fields."""
import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

client = TestClient(app)


def _register_login():
	email = "tapi@example.com"
	pwd = "Pass123!"
	r = client.post("/api/auth/register", json={"email": email, "password": pwd})
	assert r.status_code == 200
	token = r.json()["access_token"]
	return {"Authorization": f"Bearer {token}"}


def test_goal_create_status_and_queue_flow():
	headers = _register_login()
	r = client.post("/api/goal", json={"title": "Test Goal", "description": "Do X"}, headers=headers)
	assert r.status_code == 200
	data = r.json()
	assert "task_uuid" in data
	tid = data["task_uuid"]

	rs = client.get(f"/api/status/{tid}", headers=headers)
	assert rs.status_code == 200
	assert rs.json()["status"] == "created"

	# execute without approval -> 400
	re1 = client.post(f"/api/execute/{tid}", headers=headers)
	assert re1.status_code == 400

	# approve then execute
	ra = client.post(f"/api/approve/{tid}", headers=headers)
	assert ra.status_code == 200 and ra.json()["approved"] is True
	re2 = client.post(f"/api/execute/{tid}", headers=headers)
	assert re2.status_code == 200 and re2.json()["status"] == "queued"

"""Deprecated tests (pre-auth). Skipped."""
import pytest
pytest.skip("Deprecated pre-auth tests", allow_module_level=True)
