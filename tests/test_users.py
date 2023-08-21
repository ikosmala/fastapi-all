from app import schemas
from .database import client, session
import pytest
from fastapi import HTTPException


@pytest.fixture()
def test_user(client):
    user_data = {"email": "sometest@email.com", "password": "testpassword"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


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
    assert response.status_code == 200
