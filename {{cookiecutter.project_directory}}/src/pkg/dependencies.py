from fastapi import Depends
from dependency_injector.wiring import inject, Provide

from src.pkg import services
from src.pkg.containers import Application


class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


@inject
def depend_db_service(
    db_service: services.DBService = Depends(
        Provide[Application.service.database_service]
    ),
) -> services.DBService:
    return db_service


@inject
def depend_cache_service(
    cache_service: services.CacheService = Depends(
        Provide[Application.service.cache_service]
    ),
) -> services.CacheService:
    return cache_service
