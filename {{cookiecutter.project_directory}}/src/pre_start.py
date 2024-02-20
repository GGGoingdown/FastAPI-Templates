import asyncio
import traceback
from pathlib import Path
from aioredis.exceptions import ConnectionError
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger

# Customize models
try:
    from src.pkg import containers, services
    from src.config import settings
except ModuleNotFoundError:
    import sys  # noqa

    FILE = Path(__file__).resolve()

    ROOT = FILE.parents[1]  # app folder
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))  # add ROOT to PATH

    from src.pkg import containers, services
    from src.config import settings

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
async def db_connected(db_service: services.DBService):
    try:
        result = await db_service.ping()
        logger.info(f"[Database]::Ping -> {result}")

    except ConnectionRefusedError as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e

    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
async def redis_connected(cache_service: services.CacheService):
    try:
        result = await cache_service.ping()
        logger.info(f"[Cache]::Ping -> {result}")
        if not result:
            raise ConnectionRefusedError("Redis connection refused")
    except ConnectionError as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e

    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e


async def main():
    try:
        container = containers.Application()
        container.config.from_dict(settings.model_dump(mode="json"))

        await container.gateway.init_resources()

        # Connect to database
        logger.info("--- Connecting Database ---")
        db_service = container.service.database_service()
        await db_connected(db_service)

        # Connect to cache
        logger.info("--- Connecting Cache ---")
        cache_service = container.service.cache_service()
        await redis_connected(cache_service)

    finally:
        await container.gateway.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(main())
