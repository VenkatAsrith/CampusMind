"""Tests for CORS configuration and origin validation."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings


def test_cors_preflight_trusted_origin():
    """Verify that an OPTIONS preflight from a trusted origin succeeds."""
    client = TestClient(app)
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "GET" in response.headers.get("access-control-allow-methods", "")
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_actual_request_trusted_origin():
    """Verify that a GET request from a trusted origin includes CORS header."""
    client = TestClient(app)
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_untrusted_origin_rejected():
    """Verify that requests from an untrusted origin do not receive allow-origin."""
    client = TestClient(app)
    response = client.get(
        "/api/health",
        headers={"Origin": "https://malicious-campus-spoof.com"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None


def test_cors_origin_normalization():
    """Verify that whitespace and trailing slashes are correctly stripped."""
    test_settings = Settings(
        CORS_ORIGINS=" http://localhost:5173/ , http://localhost:3000/ , http://campusmind.university.edu "
    )
    origins = test_settings.cors_origins
    assert "http://localhost:5173" in origins
    assert "http://localhost:3000" in origins
    assert "http://campusmind.university.edu" in origins
    for o in origins:
        assert not o.endswith("/")
        assert not o.startswith(" ")
