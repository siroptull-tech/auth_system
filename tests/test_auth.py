"""Тесты эндпоинтов аутентификации."""
import pytest


class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": registered_user["email"],
                "username": "other",
                "password": "password123",
            },
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "other@example.com",
                "username": registered_user["username"],
                "password": "password123",
            },
        )
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "username": "user", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "username": "user", "password": "short"},
        )
        assert response.status_code == 422

    def test_register_short_username(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "username": "ab", "password": "password123"},
        )
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_wrong_password(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_wrong_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401

    def test_login_invalid_email_format(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "notanemail", "password": "password123"},
        )
        assert response.status_code == 422


class TestLogout:
    def test_logout(self, client):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert "logged out" in response.json()["message"]
