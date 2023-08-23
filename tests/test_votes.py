import pytest
from app import models


@pytest.fixture()
def test_vote(create_test_posts, session, test_user):
    new_vote = models.Vote(post_id=create_test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()


def test_vote_on_post(authorized_client, create_test_posts):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": create_test_posts[3].id, "dir": 1},
    )
    assert response.status_code == 201
    assert response.json().get("message") == "Successfully added vote"


def test_vote_twice_on_post(authorized_client, create_test_posts, test_vote):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": create_test_posts[3].id, "dir": 1},
    )
    assert response.status_code == 409


def test_delete_vote_on_post(authorized_client, test_vote, create_test_posts):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": create_test_posts[3].id, "dir": 0},
    )
    assert response.json().get("message") == "Successfully deleted vote"


def test_delete_vote_non_exist(authorized_client, create_test_posts):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": create_test_posts[3].id, "dir": 0},
    )
    assert response.status_code == 404


def test_vote_on_post_non_exist(authorized_client):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": 999999999, "dir": 1},
    )
    assert response.status_code == 404


def test_vote_on_post_user_unauth(client, create_test_posts):
    response = client.post(
        "/vote/",
        json={"post_id": create_test_posts[3].id, "dir": 1},
    )
    assert response.status_code == 401
