from app import schemas

import pytest
from fastapi import HTTPException
from jose import jwt
from app.config import settings


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_user(client):
    response = client.post(
        "/users/", json={"email": "test2@mail.com", "password": "testpass"}
    )
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "test2@mail.com"
    assert response.status_code == 201


def test_create_same_user_twice(client, test_user):
    response = client.post(
        "/users/", json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert response.status_code == 409
    assert "already exists" in response.json().get("detail")


@pytest.mark.parametrize(
    "email, password, result",
    [
        ("valid@email.com", "validpassword", 201),
        ("invalid-email.com", "validpassword", 422),
        ("valid@email.com", "", 422),
    ],
)
def test_invalid_user_data(client, email, password, result):
    response = client.post("/users/", json={"email": email, "password": password})
    assert response.status_code == result


def test_user_login(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = schemas.Token(**response.json())

    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("sometest@email.com", "wrongpassword", 403),
        ("wrongemail@mail.com", "testpassword", 403),
        (None, None, 422),
        (None, "testpassword", 422),
        ("sometest@email.com", None, 422),
    ],
)
def test_incorrect_login(client, test_user, email, password, status_code):
    response = client.post(
        "/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == status_code
