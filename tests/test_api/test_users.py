from auth import verify_password
from app.models import User


def test_create_user_success(db_session, client):
    # Act
    response = client.post(
        "/api/v1/users",
        json={"login": "alice", "password": "password123"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["login"] == "alice"
    assert "password" not in response.json()

    user = db_session.query(User).filter(User.login == "alice").first()
    assert user is not None
    assert verify_password("password123", user.password_hash)


def test_create_user_duplicate_login(user_factory, client):
    # Arrange
    user_factory(login="alice")

    # Act
    response = client.post(
        "/api/v1/users",
        json={"login": "alice", "password": "password123"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_create_user_password_too_short(client):
    # Act
    response = client.post(
        "/api/v1/users",
        json={"login": "alice", "password": "short"},
    )

    # Assert
    assert response.status_code == 422


def test_get_me_success(user_factory, auth_headers, client):
    # Arrange
    user = user_factory(login="alice")

    # Act
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"id": user.id, "login": "alice"}


def test_get_me_unauthorized(client):
    # Act
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer notexists"},
    )

    # Assert
    assert response.status_code == 401


def test_login_for_access_token_success(user_factory, client):
    # Arrange
    user_factory(login="alice", password="password123")

    # Act
    response = client.post(
        "/api/v1/users/token",
        data={"username": "alice", "password": "password123"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_for_access_token_wrong_password(user_factory, client):
    # Arrange
    user_factory(login="alice", password="password123")

    # Act
    response = client.post(
        "/api/v1/users/token",
        data={"username": "alice", "password": "wrongpassword"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
