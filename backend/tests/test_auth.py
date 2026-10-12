def test_register_success(client):
    payload = {
        "email": "newuser@studypilot.io",
        "password": "SecurePassword123!",
        "full_name": "New Student",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    # Check cookies
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_register_duplicate_email(client, user_a):
    payload = {
        "email": user_a.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate Student",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "CONFLICT"


def test_register_invalid_password(client):
    payload = {
        "email": "shortpass@studypilot.io",
        "password": "short",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_login_success(client, user_a):
    payload = {
        "email": user_a.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user_a):
    payload = {
        "email": user_a.email,
        "password": "IncorrectPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_refresh_token(client, user_a):
    login_res = client.post("/api/v1/auth/login", json={
        "email": user_a.email,
        "password": "Password123!",
    })
    refresh_cookie = login_res.cookies.get("refresh_token")

    # Refresh via cookie
    response = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh_cookie})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_get_me(client, user_a, auth_headers_a):
    response = client.get("/api/v1/auth/me", headers=auth_headers_a)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_a.email
    assert data["full_name"] == user_a.full_name
    assert data["is_active"] is True


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_logout(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
