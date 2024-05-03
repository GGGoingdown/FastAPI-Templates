import pytest
from fastapi import FastAPI

from src.pkg import services


@pytest.mark.asyncio
async def test_ping(app: FastAPI):
    db_service: services.DBService = app.container.service.database_service()
    result = await db_service.ping()
    assert result is True
