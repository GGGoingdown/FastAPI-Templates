import typing
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class LogLevel(str, Enum):
    trace = "TRACE"
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class EnvironmentMode(str, Enum):
    development = "development"
    production = "production"
    staging = "staging"
    testing = "testing"


class UserCreate(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": [{"email": "example@example.com", "password": "example"}]
        }
    )


class UserInDB(BaseModel):
    id: int
    email: str
    password_hash: str

    model_config = ConfigDict(from_attributes=True)


class JWTUser(BaseModel):
    id: str = Field(alias="sub", description="User ID")
    roles: typing.List = Field(alias="scopes", description="User roles")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "1",
                    "roles": ["LIVE_BROADCAST_PUBLISHER"],
                },
            ]
        },
    )


class APIResponse(BaseModel):
    detail: str = Field(description="Response message")

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "This is a message"}}
    )
