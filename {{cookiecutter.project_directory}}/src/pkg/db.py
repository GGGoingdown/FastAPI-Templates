import typing
import aioredis
from loguru import logger
from tortoise import Tortoise, connections
from dependency_injector import resources
from pydantic_core import Url

from src.config import settings, get_tortoise_config


DEFAULT_TORTOISE = get_tortoise_config(str(settings.pg_dsn))


class DatabaseResource(resources.AsyncResource):
    async def init(self, dsn: Url = None):
        config = get_tortoise_config(str(dsn)) if dsn else DEFAULT_TORTOISE
        await Tortoise.init(config=config)
        logger.debug("Database initialized")

    async def shutdown(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        await connections.close_all()
        logger.debug("Database shutdown")


class CacheResource(resources.Resource):
    def init(self, dsn: Url) -> aioredis.Redis:
        redis_client = aioredis.from_url(
            dsn,
            encoding="utf-8",
            decode_responses=True,
            # health_check_interval=30,
        )
        logger.debug("Cache initialized")
        return redis_client

    def shutdown(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        logger.debug("Cache shutdown")
