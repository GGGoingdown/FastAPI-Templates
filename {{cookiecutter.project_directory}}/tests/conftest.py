import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from tortoise import Tortoise, generate_schema_for_client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    return loop


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_tests(event_loop):
    from src.pkg.db import get_tortoise_config
    from src.config import settings

    TORTOISE_TEST_ORM = get_tortoise_config(settings.pg_dsn)
    await Tortoise.init(config=TORTOISE_TEST_ORM)
    await Tortoise.generate_schemas()
    await generate_schema_for_client(Tortoise.get_connection("default"), safe=True)


@pytest.fixture()
def app():
    from src.main import create_app

    app = create_app()
    yield app
    app.container.unwire()


@pytest_asyncio.fixture()
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
