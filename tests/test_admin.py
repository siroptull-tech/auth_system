"""Тесты эндпоинтов администрирования (роли, доступы)."""
import pytest


@pytest.fixture
def role_id(client, auth_headers):
    """Создаёт роль и возвращает её id."""
    response = client.post(
        "/api/v1/admin/roles",
        json={"name": "testrole", "description": "Test role"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


class TestRolesAPI:
    def test_create_role(self, client, auth_headers):
        response = client.post(
            "/api/v1/admin/roles",
            json={"name": "moderator", "description": "Moderator"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "moderator"
        assert "id" in data

    def test_create_role_unauthorized(self, client):
        response = client.post("/api/v1/admin/roles", json={"name": "x"})
        assert response.status_code == 401

    def test_list_roles(self, client, auth_headers, role_id):
        response = client.get("/api/v1/admin/roles", headers=auth_headers)
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        assert any(r["id"] == role_id for r in roles)

    def test_get_role(self, client, auth_headers, role_id):
        response = client.get(f"/api/v1/admin/roles/{role_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == role_id

    def test_get_role_not_found(self, client, auth_headers):
        response = client.get("/api/v1/admin/roles/99999", headers=auth_headers)
        assert response.status_code == 404


class TestAssignRole:
    def test_assign_role_to_user(self, client, auth_headers, role_id):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.post(
            f"/api/v1/admin/users/{me['id']}/roles/{role_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "assigned" in response.json()["message"]

    def test_assign_same_role_twice(self, client, auth_headers, role_id):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        client.post(f"/api/v1/admin/users/{me['id']}/roles/{role_id}", headers=auth_headers)
        response = client.post(
            f"/api/v1/admin/users/{me['id']}/roles/{role_id}",
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_assign_role_user_not_found(self, client, auth_headers, role_id):
        response = client.post(
            f"/api/v1/admin/users/99999/roles/{role_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_assign_role_role_not_found(self, client, auth_headers):
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        response = client.post(
            f"/api/v1/admin/users/{me['id']}/roles/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestAccessControlAPI:
    def test_create_access_control(self, client, auth_headers, role_id):
        response = client.post(
            "/api/v1/admin/permissions",
            json={
                "role_id": role_id,
                "resource_type": "invoices",
                "can_read": True,
                "can_create": False,
                "can_update": False,
                "can_delete": False,
                "can_read_all": False,
                "can_export": False,
                "can_admin": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["can_read"] is True
        assert data["resource_type"] == "invoices"

    def test_create_access_control_role_not_found(self, client, auth_headers):
        response = client.post(
            "/api/v1/admin/permissions",
            json={"role_id": 99999, "resource_type": "x"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_list_access_controls(self, client, auth_headers, role_id):
        client.post(
            "/api/v1/admin/permissions",
            json={"role_id": role_id, "resource_type": "reports", "can_read": True},
            headers=auth_headers,
        )
        response = client.get("/api/v1/admin/permissions", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_access_controls_filter_by_role(self, client, auth_headers, role_id):
        response = client.get(
            f"/api/v1/admin/permissions?role_id={role_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_access_control(self, client, auth_headers, role_id):
        created = client.post(
            "/api/v1/admin/permissions",
            json={"role_id": role_id, "resource_type": "contracts"},
            headers=auth_headers,
        ).json()
        response = client.get(
            f"/api/v1/admin/permissions/{created['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_access_control_not_found(self, client, auth_headers):
        response = client.get("/api/v1/admin/permissions/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_toggle_permission(self, client, auth_headers, role_id):
        created = client.post(
            "/api/v1/admin/permissions",
            json={"role_id": role_id, "resource_type": "toggle", "can_read": False},
            headers=auth_headers,
        ).json()
        response = client.patch(
            f"/api/v1/admin/permissions/{created['id']}?permission=read",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_toggle_permission_not_found(self, client, auth_headers):
        response = client.patch(
            "/api/v1/admin/permissions/99999?permission=read",
            headers=auth_headers,
        )
        assert response.status_code == 404
