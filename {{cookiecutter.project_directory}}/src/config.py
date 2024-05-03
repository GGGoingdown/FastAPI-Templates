import ssl
from typing import Optional, Dict, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, PostgresDsn, RedisDsn, AmqpDsn
from pydantic_core import Url
from functools import lru_cache
from kombu import Queue

from src.pkg import schema


class Settings(BaseSettings):
    # Application Settings from environment
    app_name: str = Field(
        "{{ cookiecutter.project_slug }}", validation_alias="APP_NAME"
    )
    environment: schema.EnvironmentMode = Field(
        schema.EnvironmentMode.development, validation_alias="ENVIRONMENT"
    )
    # Log
    log_path: str = Field("./logs", validation_alias="APP_LOG_PATH")
    show_log_level: schema.LogLevel = Field(
        schema.LogLevel.debug, validation_alias="APP_SHOW_LOG_LEVEL"
    )
    write_log_level: schema.LogLevel = Field(
        schema.LogLevel.warning, validation_alias="APP_WRITE_LOG_LEVEL"
    )

    admin_username: str = Field("admin", validation_alias="ADMIN_USERNAME")
    admin_password: str = Field("admin", validation_alias="ADMIN_PASSWORD")

    # Sentry
    sentry_dsn: Optional[HttpUrl] = Field(None, validation_alias="SENTRY_DSN")
    sentry_sample_rate: float = Field(1.0, validation_alias="SENTRY_SAMPLE_RATE")
    sentry_enable_tracing: bool = Field(False, validation_alias="SENTRY_ENABLE_TRACING")

    # JWT
    jwt_secret_key: str = Field(validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(validation_alias="JWT_ALGORITHM")
    jwt_expire_min: int = Field(10, validation_alias="JWT_EXPIRE_TIME_MINUTE")

    # Postgres
    pg_dsn: PostgresDsn = Field(..., validation_alias="PG_DSN")

    # Redis
    redis_dsn: RedisDsn = Field(..., validation_alias="REDIS_DSN")

    # Celery
    celery_broker_dsn: Union[RedisDsn, AmqpDsn] = Field(
        ..., validation_alias="CELERY_BROKER_DSN"
    )
    celery_result_backend_dsn: RedisDsn = Field(
        ..., validation_alias="CELERY_RESULT_BACKEND_DSN"
    )

    model_config = SettingsConfigDict(
        env_file="/mnt/secret/.env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache(maxsize=50)
def get_settings() -> Settings:
    return Settings()


# DB
def get_tortoise_config(db_url: Union[str, Url]) -> Dict:
    db_model_list = ["src.pkg.models"]
    config = {
        "connections": {"default": str(db_url)},
        "apps": {
            "models": {
                "models": [*db_model_list, "aerich.models"],
                "default_connection": "default",
            },
        },
    }
    return config


settings = get_settings()


# Celery Configuration
class CeleryConfiguration:
    broker_url = str(settings.celery_broker_dsn)
    result_backend = str(settings.celery_result_backend_dsn)

    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]

    task_queues = (Queue("hight"), Queue("low"))
    task_default_queue = "low"
    task_default_exchange = "ocr"
    task_default_exchange_type = "direct"

    worker_send_task_event = False

    broker_connection_retry_on_startup = True

    if str(settings.celery_result_backend_dsn).startswith("rediss"):
        broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
        redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

    if settings.environment == schema.EnvironmentMode.testing:
        task_always_eager = True
