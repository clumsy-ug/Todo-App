import os
import tempfile
import pytest
from app import app, db, User, Todo
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["TESTING"] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


def test_get_todos_with_authentication(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    client.post(
        "/todos",
        json={"content": "Test Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/todos", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["content"] == "Test Todo"


def test_add_todo_with_authentication(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    response = client.post(
        "/todos",
        json={"content": "Test Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["content"] == "Test Todo"


def test_add_todo_without_content(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    response = client.post(
        "/todos",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json["error"] == "Bad Request"
    assert response.json["message"] == "Content is required"


def test_delete_todo_with_authentication(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    add_response = client.post(
        "/todos",
        json={"content": "Test Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = add_response.json["id"]

    delete_response = client.delete(
        f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json["content"] == "Test Todo"


def test_delete_nonexistent_todo(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    response = client.delete(
        "/todos/9999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_update_todo_with_authentication(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    add_response = client.post(
        "/todos",
        json={"content": "Test Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = add_response.json["id"]

    update_response = client.put(
        f"/todos/{todo_id}",
        json={"content": "Updated Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json["content"] == "Updated Todo"


def test_update_todo_without_content(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    add_response = client.post(
        "/todos",
        json={"content": "Test Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = add_response.json["id"]

    update_response = client.put(
        f"/todos/{todo_id}",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 400
    assert update_response.json["error"] == "Bad Request"
    assert update_response.json["message"] == "Content is required"


def test_update_nonexistent_todo(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json["access_token"]

    response = client.put(
        "/todos/9999",
        json={"content": "Updated Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_register(client):
    response = client.post(
        "/register", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 201
    assert response.json["msg"] == "Registration successful"


def test_register_missing_data(client):
    response = client.post("/register", json={})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing username and password"

    response = client.post("/register", json={"username": "testuser"})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing password"

    response = client.post("/register", json={"password": "testpass"})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing username"


def test_register_existing_username(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = client.post(
        "/register", json={"username": "testuser", "password": "newpass"}
    )
    assert response.status_code == 400
    assert response.json["msg"] == "Username already exists"


def test_login(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json


def test_login_incorrect_credentials(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = client.post(
        "/login", json={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json["msg"] == "Bad username or password"

    response = client.post(
        "/login", json={"username": "nonexistent", "password": "testpass"}
    )
    assert response.status_code == 401
    assert response.json["msg"] == "Bad username or password"
