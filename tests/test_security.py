"""Тесты модуля безопасности (JWT, хэширование паролей)."""
import time
from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert len(hashed) > 20

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_different_each_time(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2  # bcrypt использует соль


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token({"user_id": 1, "email": "user@example.com"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "user@example.com"

    def test_token_with_custom_expiry(self):
        token = create_access_token(
            {"user_id": 1}, expires_delta=timedelta(hours=2)
        )
        payload = decode_token(token)
        assert payload is not None

    def test_expired_token(self):
        token = create_access_token(
            {"user_id": 1}, expires_delta=timedelta(seconds=-1)
        )
        payload = decode_token(token)
        assert payload is None

    def test_invalid_token(self):
        payload = decode_token("completely.invalid.token")
        assert payload is None

    def test_tampered_token(self):
        token = create_access_token({"user_id": 1})
        tampered = token[:-5] + "XXXXX"
        payload = decode_token(tampered)
        assert payload is None
