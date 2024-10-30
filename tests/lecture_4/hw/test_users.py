import base64
from datetime import datetime
from http import HTTPStatus
from typing import Any

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserService, UserInfo, UserRole, password_is_longer_than_8

app = create_app()

@pytest.fixture()
def client():
    """Фикстура для создания клиента FastAPI и инициализации UserService."""
    with TestClient(app) as client:
        yield client
    

@pytest.fixture()
def admin_creds():
    return base64.b64encode(f"admin:superSecretAdminPassword123".encode("ascii")).decode("utf-8")


@pytest.fixture(scope='function')
def existing_user(client) -> dict[str, Any]:
    response = client.post("/user-register",
                           json={
                               "username": "testuser",
                               "name": "Test User",
                               "birthdate": "2000-01-01T00:00:00",
                               "role": UserRole.USER,
                               "password": "AnotherValidPassword123"
                           })
    return response.json()


@pytest.mark.parametrize(
    ("body", "status_code"),
    [
        (
            {"id": "2"},
            HTTPStatus.OK,
        ),
        (
            {"username": "testuser"},
            HTTPStatus.OK,
        ),
        (
            {"id": "2",
             "username": "testuser"},
            HTTPStatus.BAD_REQUEST,
        ),
        (
            {},
            HTTPStatus.BAD_REQUEST,
        ),
        (
            {"username": "nonexistentuser"},
            HTTPStatus.NOT_FOUND,
        ),
    ],
)
def test_get_user(client, admin_creds, existing_user, body, status_code):
    """Тест регистрации нового пользователя и проверки на существующего."""
    response = client.post("/user-get", params=body, headers={"Authorization": "Basic " + admin_creds})
    print(response.text)
    json = response.json()
    assert response.status_code == status_code
    
    if response.status_code == 200:
        assert json["username"] == existing_user["username"]
        assert json["name"] == existing_user["name"]
        assert json["birthdate"] == existing_user["birthdate"]

def test_user_get_with_invalid_password(client, existing_user):
    creds = base64.b64encode(f"admin:wrong-password".encode("ascii")).decode("utf-8")
    response = client.post(
        "/user-get",
        params={'id': existing_user['uid']},
        headers={"Authorization": "Basic " + creds},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

@pytest.mark.parametrize(
    ("user", "body", "status_code"),
    [
        (
            "new_user",
            {"username": "testuser_2",
             "name": "Test User",
             "birthdate": "2000-01-01T00:00:00",
             "password": "ValidPassword123"},
            HTTPStatus.OK,
        ),
        (
            "existing_user",
            {"username": "testuser",
             "name": "Test User",
             "birthdate": "2000-01-01T00:00:00",
             "password": "AnotherValidPassword123"},
            HTTPStatus.BAD_REQUEST,
        ),
        (
            "short_pass",
            {"username": "testuser",
             "name": "Test User",
             "birthdate": "2000-01-01T00:00:00",
             "password": "Short"},
            HTTPStatus.BAD_REQUEST,
        ),
    ],
)
def test_user_registration(client, existing_user, user, body, status_code):
    """Тест регистрации нового пользователя и проверки на существующего."""

    response = client.post("/user-register", json=body)
    json = response.json()
    assert response.status_code == status_code
    
    if response.status_code == 200:
        assert json["username"] == body["username"]
        assert json["name"] == body["name"]
        assert json["birthdate"] == body["birthdate"]


@pytest.mark.parametrize(
    ("name", "body", "status_code"),
    [
        (
            "correct",
            {"id": "2"},
            HTTPStatus.OK,
        ),
        (
            "wrong_cred",
            {"id": "2"},
            HTTPStatus.FORBIDDEN,
        ),
        (
            "unknown_user",
            {"id": "23"},
            HTTPStatus.BAD_REQUEST,
        ),
    ],
)
def test_user_promote(request, client, admin_creds, existing_user, name, body, status_code):
    """Тест регистрации нового пользователя и проверки на существующего."""
    if name == "wrong_cred":
        creds = base64.b64encode(f"testuser:AnotherValidPassword123".encode("ascii")).decode("utf-8")
    else:
        creds = admin_creds

    response = client.post('/user-promote', params=body, headers={"Authorization": "Basic " + creds})
    assert response.status_code == status_code


