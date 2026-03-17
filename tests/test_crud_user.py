"""Тесты CRUD операций с пользователями."""
import pytest

from app.crud.user import (
    create_user,
    delete_user,
    get_all_active_users,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    soft_delete_user,
    update_user,
)
from app.schemas.user import UserCreate, UserUpdate


@pytest.fixture
def sample_user_data():
    return UserCreate(
        email="crud@example.com",
        username="cruduser",
        password="password123",
        full_name="CRUD User",
    )


@pytest.fixture
def created_user(db, sample_user_data):
    return create_user(db, sample_user_data)


class TestCreateUser:
    def test_create_user_success(self, db, sample_user_data):
        user = create_user(db, sample_user_data)
        assert user.id is not None
        assert user.email == sample_user_data.email
        assert user.username == sample_user_data.username
        assert user.full_name == sample_user_data.full_name
        assert user.hashed_password != sample_user_data.password
        assert user.is_active is True

    def test_create_user_without_full_name(self, db):
        data = UserCreate(email="noname@example.com", username="noname", password="password123")
        user = create_user(db, data)
        assert user.full_name is None


class TestGetUser:
    def test_get_by_email(self, db, created_user):
        user = get_user_by_email(db, created_user.email)
        assert user is not None
        assert user.id == created_user.id

    def test_get_by_email_not_found(self, db):
        user = get_user_by_email(db, "nonexistent@example.com")
        assert user is None

    def test_get_by_username(self, db, created_user):
        user = get_user_by_username(db, created_user.username)
        assert user is not None
        assert user.id == created_user.id

    def test_get_by_username_not_found(self, db):
        user = get_user_by_username(db, "nonexistent")
        assert user is None

    def test_get_by_id(self, db, created_user):
        user = get_user_by_id(db, created_user.id)
        assert user is not None
        assert user.email == created_user.email

    def test_get_by_id_not_found(self, db):
        user = get_user_by_id(db, 99999)
        assert user is None

    def test_get_all_active_users(self, db, created_user):
        users = get_all_active_users(db)
        assert len(users) >= 1
        assert all(u.is_active for u in users)

    def test_get_all_users_pagination(self, db, created_user):
        users = get_all_active_users(db, skip=0, limit=1)
        assert len(users) == 1


class TestUpdateUser:
    def test_update_full_name(self, db, created_user):
        updated = update_user(db, created_user.id, UserUpdate(full_name="New Name"))
        assert updated.full_name == "New Name"

    def test_update_password(self, db, created_user):
        old_hash = created_user.hashed_password
        updated = update_user(db, created_user.id, UserUpdate(password="newpassword"))
        assert updated.hashed_password != old_hash

    def test_update_nonexistent_user(self, db):
        result = update_user(db, 99999, UserUpdate(full_name="X"))
        assert result is None


class TestSoftDelete:
    def test_soft_delete_user(self, db, created_user):
        result = soft_delete_user(db, created_user.id)
        assert result.is_active is False
        # Нельзя найти по id (get_user_by_id проверяет is_active)
        assert get_user_by_id(db, created_user.id) is None

    def test_soft_delete_nonexistent(self, db):
        result = soft_delete_user(db, 99999)
        assert result is None


class TestDeleteUser:
    def test_delete_user(self, db, created_user):
        result = delete_user(db, created_user.id)
        assert result is True
        assert get_user_by_id(db, created_user.id) is None

    def test_delete_nonexistent_user(self, db):
        result = delete_user(db, 99999)
        assert result is False
