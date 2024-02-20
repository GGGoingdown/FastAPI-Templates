from typing import Optional, Dict, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, PostgresDsn, RedisDsn
from pydantic_core import Url
from functools import lru_cache

from src.pkg import schema


class Settings(BaseSettings):
    # Application Settings from environment
    app_name: str = Field(
        "{{ cookiecutter.project_slug }}", validation_alias="APP_NAME"
    )
    environment: schema.EnvironmentMode = Field(
        schema.EnvironmentMode.development, validation_alias="APP_ENVIRONMENT"
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

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
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
