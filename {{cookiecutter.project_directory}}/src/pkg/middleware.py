import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from loguru import logger


# Initialize sentry
def init_sentry(
    *,
    dsn: str,
    environment: str,
    release: str,
    sample_rate: float,
    fastapi_integration: bool = False,
    enable_tracing: bool = True,
) -> None:
    logger.info("Initialize sentry")
    integrations = []
    if fastapi_integration:
        integrations.append(FastApiIntegration(transaction_style="endpoint"))

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        sample_rate=sample_rate,
        enable_tracing=enable_tracing,
        integrations=integrations,
    )


def add_cors_middleware(app: FastAPI) -> None:
    origins = [
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8888",
        "http://localhost:8080",
        "http://localhost:8888",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
