import pytest
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasicCredentials, SecurityScopes

from src.pkg import services, schema


test_secruity_scopes = SecurityScopes()


def test_jwt_handler(app: FastAPI):
    jwt_handler: services.JWTHandler = app.container.service.jwt_handler()
    payload = schema.JWTUser(sub="1", scopes=[]).model_dump(mode="json", by_alias=True)
    token = jwt_handler.encode(payload)
    decoded_payload = jwt_handler.decode(token)
    assert decoded_payload == payload


def test_authenticate_admin(app: FastAPI):
    auth_service: services.AuthService = app.container.service.auth_service()
    credentials = HTTPBasicCredentials(
        username=auth_service.admin_username, password=auth_service.admin_password
    )
    assert auth_service.authenticate_admin(credentials) is True
    credentials = HTTPBasicCredentials(
        username=auth_service.admin_username, password="wrong_password"
    )
    assert auth_service.authenticate_admin(credentials) is False


def test_create_jwt_token(app: FastAPI):
    jwt_handler: services.JWTHandler = app.container.service.jwt_handler()
    auth_service: services.AuthService = app.container.service.auth_service()
    user_id = "123"
    token = auth_service.create_jwt_token(user_id=user_id, scopes=[])
    decoded_payload = jwt_handler.decode(token)
    assert decoded_payload["sub"] == str(user_id)


def test_authenticate_jwt(app: FastAPI):
    user_id = "123"
    auth_service: services.AuthService = app.container.service.auth_service()

    token = auth_service.create_jwt_token(user_id=user_id, scopes=[])
    user = auth_service.authenticate_jwt(token, test_secruity_scopes)
    assert user is not None
    assert user.id == user_id


def test_authenticate_invalid_jwt(app: FastAPI):
    auth_service: services.AuthService = app.container.service.auth_service()
    token = "invalid_token"
    with pytest.raises(HTTPException):
        auth_service.authenticate_jwt(token, test_secruity_scopes)


def test_jwt_invalid_payload(app: FastAPI):
    jwt_handler: services.JWTHandler = app.container.service.jwt_handler()
    auth_service: services.AuthService = app.container.service.auth_service()
    payload = {"invalid_key": "invalid_value"}
    token = jwt_handler.encode(payload)
    with pytest.raises(HTTPException):
        auth_service.authenticate_jwt(token, test_secruity_scopes)
