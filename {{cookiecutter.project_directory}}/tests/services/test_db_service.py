import pytest
from fastapi import FastAPI

from src.pkg import services, schema


@pytest.mark.asyncio
async def test_ping(app: FastAPI):
    db_service: services.DBService = app.container.service.database_service()
    result = await db_service.ping()
    assert result is True


@pytest.mark.asyncio
async def test_create_user(app: FastAPI):
    db_service: services.DBService = app.container.service.database_service()
    user = schema.UserCreate.model_validate(
        schema.UserCreate.model_json_schema()["example"][0]
    )
    auth_service: services.AuthService = app.container.service.auth_service()
    password_hash = auth_service.get_password_hash(password=user.password)

    user = await db_service.create_user(user=user, password_hash=password_hash)
    assert user is not None
