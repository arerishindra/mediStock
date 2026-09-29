"""
MediStock Backend — Auth Tests
"""


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Admin@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["email"] == "admin@test.com"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_get_me(client, admin_headers):
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "admin@test.com"
