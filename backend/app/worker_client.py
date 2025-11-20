"""Worker client helper: enqueue tasks to Redis or fallback in-memory queue."""
from typing import Any, Dict
import os
import json

REDIS_URL = os.getenv("REDIS_URL")

_in_memory_queue = []

def enqueue_task(payload: Dict[str, Any]):
    """Enqueue a task to Redis list 'phantom:tasks' if REDIS_URL present, otherwise fallback to in-memory queue.

    This design allows unit tests to run without a running Redis instance.
    TODO: replace with robust queueing (RQ/Celery) and retry semantics.
    """
    if REDIS_URL:
        try:
            import redis

            r = redis.from_url(REDIS_URL)
            r.rpush("phantom:tasks", json.dumps(payload))
            return True
        except Exception:
            # best-effort fallback
            _in_memory_queue.append(payload)
            return False
    else:
        _in_memory_queue.append(payload)
        return True

def pop_in_memory():
    if _in_memory_queue:
        return _in_memory_queue.pop(0)
    return None
