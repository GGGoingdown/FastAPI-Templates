import pytest
from unittest import mock
from fastapi import FastAPI
from httpx import AsyncClient

from src.pkg import services


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    endpoint = "/health"
    r = await client.get(endpoint)
    assert r.status_code == 200, f"Error status code: {r.json()}"


@pytest.mark.asyncio
async def test_db_health_check(app: FastAPI, client: AsyncClient):
    endpoint = "/db/health"
    # Mock the database service
    db_service_mock = mock.AsyncMock(spec=services.DBService)
    db_service_mock.ping.return_value = True

    with app.container.service.override_providers(database_service=db_service_mock):
        r = await client.get(endpoint)
        assert r.status_code == 200, f"Error status code: {r.json()}"

    db_service_mock.ping.assert_called_once()

    # Error case
    db_service_mock.reset_mock()

    db_service_mock.ping.return_value = False
    with app.container.service.override_providers(database_service=db_service_mock):
        r = await client.get(endpoint)
        assert r.status_code == 503, f"Error status code: {r.json()}"

    db_service_mock.ping.assert_called_once()


@pytest.mark.asyncio
async def test_cache_health_check(app: FastAPI, client: AsyncClient):
    endpoint = "/cache/health"

    # Mock the cache service
    cache_service_mock = mock.AsyncMock(spec=services.CacheService)
    cache_service_mock.ping.return_value = True

    with app.container.service.override_providers(cache_service=cache_service_mock):
        r = await client.get(endpoint)
        assert r.status_code == 200, f"Error status code: {r.json()}"

    cache_service_mock.ping.assert_called_once()

    # Error case
    cache_service_mock.reset_mock()

    cache_service_mock.ping.return_value = False
    with app.container.service.override_providers(cache_service=cache_service_mock):
        r = await client.get(endpoint)
        assert r.status_code == 503, f"Error status code: {r.json()}"

    cache_service_mock.ping.assert_called_once()
