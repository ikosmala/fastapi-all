from fastapi.testclient import TestClient
from app.main import app
from app import schemas
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import get_db, Base
import pytest

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_user(client):
    response = client.post(
        "/users", json={"email": "test2@mail.com", "password": "testpass"}
    )
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "test2@mail.com"
    assert response.status_code == 201
