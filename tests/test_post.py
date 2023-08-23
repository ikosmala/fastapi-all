import pytest
from app import schemas


def test_get_all_posts(authorized_client, create_test_posts):
    response = authorized_client.get("/posts/")
    posts_map = map(
        lambda post: schemas.PostOut(**post).model_dump_json(), response.json()
    )
    posts_list = list(posts_map)
    assert len(posts_list) == len(response.json())
    assert response.status_code == 200


def test_unauthorized_user_get_all_posts(client, create_test_posts):
    response = client.get("/posts/")
    assert response.status_code == 401


def test_unauthorized_user_get_one_post(client, create_test_posts):
    response = client.get(f"/posts/{create_test_posts[0].id}")
    assert response.status_code == 401


def test_nonexisting_get_one_post(authorized_client, create_test_posts):
    response = authorized_client.get(f"/posts/99999999")
    assert response.status_code == 404


def test_get_one_post(authorized_client, create_test_posts):
    response = authorized_client.get(f"/posts/{create_test_posts[0].id}")
    assert response.status_code == 200
    post = schemas.PostOut(**response.json())
    assert create_test_posts[0].id == post.Post.id
    assert create_test_posts[0].content == post.Post.content
    assert create_test_posts[0].title == post.Post.title
    assert create_test_posts[0].owner_id == post.Post.owner_id


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("test title", "test content", True),
        ("second test title", "second test content", False),
        ("third test title", "third test content", True),
    ],
)
def test_create_post(authorized_client, test_user, title, content, published):
    response = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )
    post = schemas.Post(**response.json())
    assert response.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user["id"]


def test_unauthorized_user_create_post(client):
    response = client.post(
        "/posts/", json={"title": "some title", "content": "some content"}
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "title, content, published",
    [
        (None, "test content", True),
        ("second test title", None, False),
        ("third test title", "third test content", None),
    ],
)
def test_invalid_data_create_post(authorized_client, title, content, published):
    response = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )
    assert response.status_code == 422


def test_unauth_user_delete_post(client, test_user, create_test_posts):
    response = client.delete(f"/posts/{create_test_posts[0].id}")
    assert response.status_code == 401


def test_delete_post(authorized_client, create_test_posts):
    response = authorized_client.delete(f"/posts/{create_test_posts[0].id}")
    assert response.status_code == 204


def test_delete_post_non_exist(authorized_client, create_test_posts):
    response = authorized_client.delete(f"/posts/9999999")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, create_test_posts):
    response = authorized_client.delete(f"/posts/{create_test_posts[3].id}")
    assert response.status_code == 403


def test_update_post(authorized_client, test_user, create_test_posts):
    data = {
        "title": "updated post",
        "content": "updated content",
    }
    response = authorized_client.put(f"/posts/{create_test_posts[0].id}", json=data)
    updated_post = schemas.Post(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]
    assert updated_post.owner_id == test_user["id"]


def test_update_other_user_post(authorized_client, create_test_posts):
    data = {
        "title": "updated post",
        "content": "updated content",
    }
    response = authorized_client.put(f"/posts/{create_test_posts[3].id}", json=data)
    assert response.status_code == 403


def test_update_post_unauthorized_user(client, create_test_posts):
    data = {
        "title": "updated post",
        "content": "updated content",
    }
    response = client.put(f"/posts/{create_test_posts[0].id}", json=data)
    assert response.status_code == 401


def test_update_post_non_exist(authorized_client, create_test_posts):
    data = {
        "title": "updated post",
        "content": "updated content",
    }
    response = authorized_client.put(f"/posts/99999999", json=data)
    assert response.status_code == 404
