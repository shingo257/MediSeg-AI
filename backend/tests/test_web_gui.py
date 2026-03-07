"""Smoke tests for Web GUI routes using Flask test client."""
import pytest


def test_healthz_returns_ok(web_app):
    """GET /api/healthz returns 200 and success payload."""
    client = web_app.test_client()
    r = client.get("/api/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None
    assert "success" in data


def test_version_returns_build_info(web_app):
    """GET /api/version returns 200 and build info."""
    client = web_app.test_client()
    r = client.get("/api/version")
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None
    assert data.get("success") is True
    assert "build" in data


def test_models_returns_list(web_app):
    """GET /api/models returns 200 and a list (may be empty if models not loaded)."""
    client = web_app.test_client()
    r = client.get("/api/models")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)


def test_index_returns_html_or_redirect(web_app):
    """GET / returns 200 (HTML) or 404 if template missing."""
    client = web_app.test_client()
    r = client.get("/")
    assert r.status_code in (200, 404)
