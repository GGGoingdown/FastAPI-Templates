import sys
import typing
import aioredis
import socket
import secrets
import httpx
from datetime import datetime, timedelta
from aioredis.exceptions import ConnectionError
from pathlib import Path
from loguru import logger
from tortoise import Tortoise
from dependency_injector import resources
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    before_log,
    retry_if_exception_type,
)

from src.pkg import schema, repositories, utils


class LoggerInit(resources.Resource):
    def init(
        self,
        app_name: str,
        log_path: str,
        show_log_level: schema.LogLevel = schema.LogLevel.debug,
        write_log_level: schema.LogLevel = schema.LogLevel.warning,
    ) -> None:
        logger.remove()

        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DDTHH:mm:ss}</green> | [<level>{level}</level>] | <c>{file}::{function}::{line}</c> | {message}",
            level=show_log_level,
        )

        new_log_path = Path(log_path) / f"{app_name}.log"
        logger.info(f"Save log to {str(new_log_path)}")
        logger.add(
            str(new_log_path),
            colorize=False,
            format="{time:YYYY-MM-DD at HH:mm:ss} | [<level>{level}</level>] | <c>{file}::{function}::{line}</c>  | {message}",
            rotation="12:00",
            level=write_log_level,
        )

    def shutdown(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        logger.remove()


### Authentication and Authorization
class JWTHandler:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    __slots__ = (
        "_secret_key",
        "_algorithm",
        "_expired_time_minute",
    )

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        expired_time_minute: int = 120,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expired_time_minute = expired_time_minute

    def decode(self, token: str) -> typing.Optional[typing.Dict]:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_aud": False},
            )

            return payload

        except JWTError as e:
            logger.info(f"JWT Error: {e}")
            return None

    def encode(self, payload: typing.Dict) -> str:
        encoded_jwt = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def create_expired_time(self) -> datetime:
        expried_dt = utils.utc_now_time() + timedelta(minutes=self._expired_time_minute)
        return expried_dt

    def get_expired_seconds(self) -> int:
        return self._expired_time_minute * 60


class BaseAuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)


class AuthService(BaseAuthService):
    __slots__ = ("_jwt_handler", "_admin_username", "_admin_password")

    def __init__(
        self, jwt_handler: JWTHandler, admin_username: str, admin_password: str
    ) -> None:
        self._jwt_handler = jwt_handler
        self._admin_username = admin_username
        self._admin_password = admin_password

    @property
    def admin_username(self) -> str:
        if self._admin_username == "admin":
            logger.warning('Admin username is default value "admin"')

        return self._admin_username

    @property
    def admin_password(self) -> str:
        if self._admin_password == "admin":
            logger.warning('Admin password is default value "admin"')

        return self._admin_password

    def authenticate_jwt(
        self, token: str, security_scopes: SecurityScopes
    ) -> schema.JWTUser:
        # Decode JWT
        payload = self._jwt_handler.decode(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_scopes = payload.get("scopes", [])

        try:
            user = schema.JWTUser.model_validate(payload)
        except ValidationError as e:
            logger.info(f"Model Validation Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"

        for scope in security_scopes.scopes:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

        return user

    def authenticate_admin(self, credentials: HTTPBasicCredentials) -> bool:
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = self._admin_username.encode("utf8")
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        current_password_bytes = credentials.password.encode("utf8")
        correct_password_bytes = self._admin_password.encode("utf8")
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )
        if not (is_correct_username and is_correct_password):
            return False
        return True

    def create_jwt_token(self, *, user_id: str, scopes: typing.Iterable) -> str:
        payload = schema.JWTUser(sub=user_id, scopes=scopes).model_dump(
            mode="json", by_alias=True
        )
        expried_dt = self._jwt_handler.create_expired_time()
        payload.update({"exp": expried_dt})
        return self._jwt_handler.encode(payload)


### Database and Cache Services
class BaseDatabaseService:
    def __init__(self, connection: str = "default"):
        self.conn = Tortoise.get_connection(connection)

    async def ping(self) -> bool:
        try:
            if await self.conn.execute_query("SELECT 1"):
                return True
            return False
        except socket.gaierror:
            return False
        except ConnectionRefusedError:
            return False


class BaseCacheService:
    def __init__(self, client: aioredis.Redis):
        self.client = client

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except ConnectionError:
            return False


class DBService(BaseDatabaseService):
    def __init__(self, user_repo: repositories.UserRepository):
        self._user_repo = user_repo
        super().__init__()

    async def create_user(
        self, user: schema.UserCreate, *, password_hash: str
    ) -> schema.UserInDB:
        return await self._user_repo.create(
            **user.model_dump(exclude={"password"}), password_hash=password_hash
        )


class CacheService(BaseCacheService):
    def __init__(self, client: aioredis.Redis):
        super().__init__(client)


### HTTP Agent
class HostAPIResource(resources.AsyncResource):
    async def init(self, base_url: str) -> httpx.AsyncClient:
        _base_url = base_url.rstrip("/")
        logger.debug(f"[HostAPI]::Base URL: {base_url}")
        client = httpx.AsyncClient(base_url=_base_url)
        return client

    async def shutdown(self, client: httpx.AsyncClient) -> None:
        await client.aclose()


class HostAPIAgent:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    @retry(
        retry=retry_if_exception_type(exception_types=(httpx.RequestError,)),
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        before=before_log(logger=logger, log_level="INFO"),
    )
    async def health_check(self) -> bool:
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e}")
            return False
