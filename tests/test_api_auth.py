"""API tests for authentication endpoints (/api/auth/login, /api/auth/me)."""


def test_login_success(client, student_user):
    """Verify login with correct credentials returns 200 and signed JWT."""
    response = client.post(
        "/api/auth/login",
        json={"username": "test_student", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "test_student"
    assert data["user"]["role"] == "student"


def test_login_invalid_password(client, student_user):
    """Verify login with incorrect password returns 401 Unauthorized."""
    response = client.post(
        "/api/auth/login",
        json={"username": "test_student", "password": "IncorrectPassword!"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Verify login with unknown username returns 401 Unauthorized."""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent_user", "password": "Password123!"},
    )
    assert response.status_code == 401


def test_get_current_user_profile_authenticated(client, student_headers):
    """Verify /api/auth/me returns current user details with valid token."""
    response = client.get("/api/auth/me", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_student"
    assert data["role"] == "student"


def test_get_current_user_profile_unauthorized(client):
    """Verify /api/auth/me returns 401 Unauthorized when Authorization header is absent."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401 or response.status_code == 403
