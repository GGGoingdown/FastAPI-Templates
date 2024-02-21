import typing

import celery
from celery import current_app as current_celery_app
from celery.signals import worker_process_init
from asgiref.sync import async_to_sync

from src.config import settings
from src.worker import (  # noqa: F401 (Tasks are imported for celery to discover them)
    tasks,
)
from src.pkg.containers import Application
from src.pkg import middleware


def create_celery(config) -> celery:
    celery_app = current_celery_app
    celery_app.config_from_object(config)

    return celery_app


# Inititalize
@worker_process_init.connect
def worker_initialize(*args: typing.Any, **kwargs: typing.Any) -> None:
    if settings.sentry_dsn:
        middleware.init_sentry(
            dsn=settings.sentry_dsn,
            environment=settings.environment.value,
            release=f"{settings.app_name}-worker",
            sample_rate=settings.sentry_sample_rate,
            fastapi_integration=False,
            celery_integration=True,
            enable_tracing=settings.sentry_enable_tracing,
        )

    container = Application()
    container.config.from_dict(settings.model_dump(mode="json"))
    async_to_sync(container.service.init_resources)()
