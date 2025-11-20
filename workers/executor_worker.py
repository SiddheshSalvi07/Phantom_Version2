"""Executor worker skeleton: dequeues tasks from Redis (or blocks) and posts logs back to backend.

Usage: set `REDIS_URL` and `BACKEND_URL` in environment, then run `python executor_worker.py`.
TODO: evolve to RQ/Celery with retries, metrics, and proper shutdown.
"""
import os
import time
import json
import requests
import os

REDIS_URL = os.getenv("REDIS_URL")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WORKER_TOKEN = os.getenv("WORKER_TOKEN", "devworkertoken")

def run_loop():
    if REDIS_URL:
        import redis

        r = redis.from_url(REDIS_URL)
        print("Worker connected to Redis, waiting for tasks...")
        while True:
            try:
                item = r.blpop("phantom:tasks", timeout=5)
                if item:
                    _, raw = item
                    task = json.loads(raw)
                    process_task(task)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print("Worker Redis error:", e)
                time.sleep(1)
    else:
        print("REDIS_URL not configured. Worker will exit (or implement alternative).")


def process_task(task):
    task_id = task.get("task_id")
    print(f"Processing task {task_id}")
    # TODO: implement model routing, step executor, and external integrations.
    time.sleep(1)
    # Adjust for updated API expecting task_uuid and worker token header
    worker_token = os.getenv("WORKER_TOKEN", "devworkertoken")
    log = {"task_uuid": task_id, "status": "done", "payload": {"note": "simulated run"}}
    try:
        r = requests.post(f"{BACKEND_URL}/api/worker/log", json=log, headers={"X-Worker-Token": worker_token}, timeout=5)
        print("Posted log to backend:", r.status_code, r.text)
    except Exception as e:
        print("Failed to post log to backend:", e)


if __name__ == "__main__":
    run_loop()
