from fastapi import APIRouter, HTTPException, status, Depends

from src.pkg import services, dependencies

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"detail": "ok"}


@router.get("/db/health")
async def db_health_check(
    db_service: services.DBService = Depends(dependencies.depend_db_service),
):
    result = await db_service.ping()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available",
        )
    return {"detail": "ok"}


@router.get("/cache/health")
async def cache_health_check(
    cache_service: services.CacheService = Depends(dependencies.depend_cache_service),
):
    result = await cache_service.ping()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache is not available",
        )
    return {"detail": "ok"}
