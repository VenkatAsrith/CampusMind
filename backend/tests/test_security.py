"""Unit tests for password hashing and JWT token operations."""

import time
import pytest
import jwt
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings


def test_password_hashing_and_verification():
    """Verify that Argon2id generates valid hashes and correctly verifies passwords."""
    plain = "SuperSecurePassword123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert hashed.startswith("$argon2")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_empty_password_rejection():
    """Verify empty passwords raise ValueError."""
    with pytest.raises(ValueError):
        get_password_hash("")


def test_jwt_creation_and_decoding():
    """Verify JWT payload claims, roles, and subject."""
    token = create_access_token(subject="user_123", role="faculty")
    payload = decode_access_token(token)

    assert payload["sub"] == "user_123"
    assert payload["role"] == "faculty"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_tampering_rejection():
    """Verify tampered JWT signature is rejected."""
    token = create_access_token(subject="user_123", role="student")
    tampered_token = token[:-4] + "abcd"

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered_token)


def test_jwt_expiration_handling():
    """Verify expired token raises ExpiredSignatureError."""
    token = create_access_token(
        subject="user_123",
        role="student",
        expires_delta=timedelta(seconds=-10),  # Expired 10 seconds ago
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
