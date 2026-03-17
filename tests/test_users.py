"""Тесты эндпоинтов пользователей."""
import pytest


class TestGetProfile:
    def test_get_own_profile(self, client, registered_user, auth_headers):
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["username"] == registered_user["username"]

    def test_get_profile_unauthorized(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401


class TestGetUser:
    def test_get_user_by_id(self, client, registered_user, auth_headers):
        # Получаем свой профиль чтобы узнать свой id
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.get(f"/api/v1/users/{me['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == me["id"]

    def test_get_nonexistent_user(self, client, auth_headers):
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_user_unauthorized(self, client):
        response = client.get("/api/v1/users/1")
        assert response.status_code == 401


class TestListUsers:
    def test_list_users(self, client, registered_user, auth_headers):
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    def test_list_users_unauthorized(self, client):
        response = client.get("/api/v1/users")
        assert response.status_code == 401


class TestUpdateUser:
    def test_update_own_profile(self, client, registered_user, auth_headers):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.put(
            f"/api/v1/users/{me['id']}",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_password(self, client, registered_user, auth_headers):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.put(
            f"/api/v1/users/{me['id']}",
            json={"password": "newpassword123"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        # Новый пароль должен работать
        login = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "newpassword123"},
        )
        assert login.status_code == 200

    def test_update_other_user_forbidden(self, client, registered_user, auth_headers):
        # Регистрируем второго пользователя
        client.post(
            "/api/v1/auth/register",
            json={"email": "other@example.com", "username": "otheruser", "password": "password123"},
        )
        response = client.put(
            "/api/v1/users/99999",
            json={"full_name": "Hacked"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_update_unauthorized(self, client):
        response = client.put("/api/v1/users/1", json={"full_name": "x"})
        assert response.status_code == 401


class TestDeleteUser:
    def test_delete_own_account(self, client, registered_user, auth_headers):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.delete(f"/api/v1/users/{me['id']}", headers=auth_headers)
        assert response.status_code == 200
        # После деактивации логин возвращает 403 (аккаунт неактивен)
        login = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
        assert login.status_code == 403

    def test_delete_other_user_forbidden(self, client, registered_user, auth_headers):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.delete(f"/api/v1/users/{me['id'] + 1}", headers=auth_headers)
        assert response.status_code == 403

    def test_delete_unauthorized(self, client):
        response = client.delete("/api/v1/users/1")
        assert response.status_code == 401
