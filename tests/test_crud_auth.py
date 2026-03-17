"""Тесты CRUD операций с ролями, разрешениями и правами доступа."""
import pytest

from app.crud.auth import (
    create_access_control,
    create_business_element,
    create_permission,
    create_role,
    get_access_control_by_id,
    get_access_control_by_role_and_resource,
    get_access_controls_by_role,
    get_all_business_elements,
    get_all_permissions,
    get_all_roles,
    get_business_element_by_id,
    get_business_element_by_name,
    get_permission_by_id,
    get_role_by_id,
    get_role_by_name,
    toggle_access_permission,
    update_access_control,
)
from app.schemas.access import (
    AccessControlCreate,
    AccessControlUpdate,
    BusinessElementCreate,
    PermissionCreate,
    RoleCreate,
)


@pytest.fixture
def role(db):
    return create_role(db, RoleCreate(name="editor", description="Editor role"))


@pytest.fixture
def business_element(db):
    return create_business_element(
        db, BusinessElementCreate(name="invoices", description="Invoices", resource_type="invoices")
    )


class TestRoleCRUD:
    def test_create_role(self, db):
        r = create_role(db, RoleCreate(name="manager", description="Manager"))
        assert r.id is not None
        assert r.name == "manager"
        assert r.is_active is True

    def test_get_role_by_id(self, db, role):
        r = get_role_by_id(db, role.id)
        assert r.name == role.name

    def test_get_role_by_id_not_found(self, db):
        assert get_role_by_id(db, 99999) is None

    def test_get_role_by_name(self, db, role):
        r = get_role_by_name(db, role.name)
        assert r.id == role.id

    def test_get_role_by_name_not_found(self, db):
        assert get_role_by_name(db, "nonexistent") is None

    def test_get_all_roles(self, db, role):
        roles = get_all_roles(db)
        assert len(roles) >= 1


class TestPermissionCRUD:
    def test_create_permission(self, db):
        p = create_permission(
            db,
            PermissionCreate(
                name="read invoice",
                action="read",
                description="Can read",
            ),
        )
        assert p.id is not None
        assert p.action == "read"

    def test_get_permission_by_id(self, db):
        p = create_permission(
            db, PermissionCreate(name="write", action="write")
        )
        found = get_permission_by_id(db, p.id)
        assert found.id == p.id

    def test_get_permission_not_found(self, db):
        assert get_permission_by_id(db, 99999) is None

    def test_get_all_permissions(self, db):
        create_permission(db, PermissionCreate(name="p1", action="read"))
        all_p = get_all_permissions(db)
        assert len(all_p) >= 1


class TestBusinessElementCRUD:
    def test_create_business_element(self, db):
        el = create_business_element(
            db, BusinessElementCreate(name="orders", description="Orders", resource_type="orders")
        )
        assert el.id is not None
        assert el.name == "orders"

    def test_get_by_id(self, db, business_element):
        found = get_business_element_by_id(db, business_element.id)
        assert found.name == business_element.name

    def test_get_by_id_not_found(self, db):
        assert get_business_element_by_id(db, 99999) is None

    def test_get_by_name(self, db, business_element):
        found = get_business_element_by_name(db, business_element.name)
        assert found.id == business_element.id

    def test_get_all(self, db, business_element):
        elements = get_all_business_elements(db)
        assert len(elements) >= 1


class TestAccessControlCRUD:
    def test_create_access_control(self, db, role):
        ac = create_access_control(
            db,
            AccessControlCreate(
                role_id=role.id,
                resource_type="invoices",
                can_read=True,
                can_create=False,
            ),
        )
        assert ac.id is not None
        assert ac.can_read is True

    def test_create_access_control_duplicate_returns_existing(self, db, role):
        payload = AccessControlCreate(role_id=role.id, resource_type="invoices", can_read=True)
        ac1 = create_access_control(db, payload)
        ac2 = create_access_control(db, payload)
        assert ac1.id == ac2.id

    def test_get_by_id(self, db, role):
        ac = create_access_control(
            db, AccessControlCreate(role_id=role.id, resource_type="reports")
        )
        found = get_access_control_by_id(db, ac.id)
        assert found.id == ac.id

    def test_get_by_id_not_found(self, db):
        assert get_access_control_by_id(db, 99999) is None

    def test_get_by_role_and_resource(self, db, role):
        create_access_control(
            db, AccessControlCreate(role_id=role.id, resource_type="documents")
        )
        found = get_access_control_by_role_and_resource(db, role.id, "documents")
        assert found is not None

    def test_get_by_role_and_resource_not_found(self, db, role):
        found = get_access_control_by_role_and_resource(db, role.id, "nonexistent")
        assert found is None

    def test_get_access_controls_by_role(self, db, role):
        create_access_control(db, AccessControlCreate(role_id=role.id, resource_type="invoices"))
        controls = get_access_controls_by_role(db, role.id)
        assert len(controls) >= 1

    def test_update_access_control(self, db, role):
        ac = create_access_control(
            db, AccessControlCreate(role_id=role.id, resource_type="contracts")
        )
        updated = update_access_control(db, ac.id, AccessControlUpdate(can_read=True, can_create=True))
        assert updated.can_read is True
        assert updated.can_create is True

    def test_update_access_control_not_found(self, db):
        result = update_access_control(db, 99999, AccessControlUpdate(can_read=True))
        assert result is None

    def test_toggle_permission(self, db, role):
        ac = create_access_control(
            db,
            AccessControlCreate(role_id=role.id, resource_type="toggle_test", can_read=False),
        )
        assert ac.can_read is False
        toggled = toggle_access_permission(db, ac.id, "read")
        assert toggled.can_read is True
        toggled2 = toggle_access_permission(db, ac.id, "read")
        assert toggled2.can_read is False

    def test_toggle_permission_not_found(self, db):
        result = toggle_access_permission(db, 99999, "read")
        assert result is None
