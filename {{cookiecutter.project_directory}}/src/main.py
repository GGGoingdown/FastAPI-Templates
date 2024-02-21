from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger

try:
    from src.config import settings, CeleryConfiguration
    from src.pkg import middleware
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    FILE = Path(__file__).resolve()
    print(sys.path)
    ROOT = FILE.parents[1]  # app folder
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))  # add ROOT to PATH

    from src.config import settings, CeleryConfiguration  # noqa: F401
    from src.pkg import middleware


__TITLE__ = "{{ cookiecutter.project_name }}"
__DESCRIPTION__ = "{{ cookiecutter.project_description }}"
__VERSION__ = "0.1.0"


def add_routers(app: FastAPI) -> None:
    # Register api
    from src import router

    # Health check
    app.include_router(
        router.health_router, tags=["Health check"], include_in_schema=True
    )


# Exceptions
def add_exceptions(app: FastAPI) -> None:
    import httpx
    from tortoise.exceptions import DoesNotExist, IntegrityError

    @app.exception_handler(httpx.HTTPError)
    async def httpx_error_handler(request: Request, exc: httpx.HTTPError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal api request error"},
            headers={"X-Error": str(exc)},
        )

    @app.exception_handler(DoesNotExist)
    async def doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(IntegrityError)
    async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
            headers={"X-Error": "IntegrityError"},
        )


# Add dependencies injection
def init_dependencies_inject(app: FastAPI) -> None:
    import sys
    from src.pkg import containers, dependencies
    from src.worker import tasks

    container = containers.Application()
    container.config.from_dict(settings.model_dump(mode="json"))
    container.wire(
        modules=[
            sys.modules[__name__],
            dependencies,
            tasks,
        ]
    )

    app.container = container


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Start application ===")
    # Init database and cache
    await app.container.service.init_resources()

    # Init sentry
    if settings.sentry_dsn:
        middleware.init_sentry(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=f"{settings.app_name}@{__VERSION__}",
            sample_rate=settings.sentry_sample_rate,
            enable_tracing=settings.sentry_enable_tracing,
            fastapi_integration=True,
        )

    yield
    logger.info("=== Shutdown application ===")
    await app.container.gateway.shutdown_resources()


# Create main app
def create_app() -> FastAPI:
    app = FastAPI(
        title=__TITLE__,
        description=__DESCRIPTION__,
        version=__VERSION__,
        lifespan=lifespan,
    )

    from src.worker import create_celery

    # Create celery
    app.celery_app = create_celery(config=CeleryConfiguration)

    init_dependencies_inject(app)

    # Register routers
    add_routers(app)

    # Add exceptions
    add_exceptions(app)

    # Add middleware
    middleware.add_cors_middleware(app)

    return app


def run_worker():
    import subprocess

    subprocess.call(
        [
            "celery",
            "-A",
            "src.main.celery",
            "worker",
            "-c",
            "1",
            "--loglevel=info",
            "-E",
            "--without-heartbeat",
            "--without-gossip",
            "--without-mingle",
            "-Ofair",
        ]
    )


def celery_watchgod():
    from watchgod import run_process

    run_process("./src", run_worker)


app = create_app()
celery = app.celery_app


if __name__ == "__main__":
    celery_watchgod()
