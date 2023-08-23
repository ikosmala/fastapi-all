from fastapi.testclient import TestClient
from app.main import app
from app import models
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import get_db, Base
import pytest
from app.oath2 import create_access_token

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# fixture for database related action
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# database session for creating test client with db connection
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# create test user fixture
@pytest.fixture()
def test_user(client):
    user_data = {"email": "sometest@email.com", "password": "testpassword"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def test_user2(client):
    user_data = {"email": "sometest2@email.com", "password": "testpassword2"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"bearer {token}"}

    return client


# test posts
@pytest.fixture()
def create_test_posts(test_user, test_user2, session):
    test_posts = [
        {"title": "1st post", "content": "1st content", "owner_id": test_user["id"]},
        {"title": "2nd post", "content": "2nd content", "owner_id": test_user["id"]},
        {"title": "3rd post", "content": "3rd content", "owner_id": test_user["id"]},
        {"title": "4th post", "content": "4th content", "owner_id": test_user2["id"]},
    ]

    post_map = map(lambda post: models.Post(**post), test_posts)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()
    return session.query(models.Post).all()
