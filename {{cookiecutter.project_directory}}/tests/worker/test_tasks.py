from src.worker import tasks
from fastapi import FastAPI


def test_health_check_task(app: FastAPI):
    result = tasks.health_check()
    assert result == {"detail": "ok"}, f"Error response: {result}"
