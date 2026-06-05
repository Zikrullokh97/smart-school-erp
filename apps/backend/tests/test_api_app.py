from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from smart_school.app import create_app
from smart_school.auth.dependencies import get_current_tenant


def dummy_tenant() -> SimpleNamespace:
    return SimpleNamespace(
        id="00000000-0000-0000-0000-000000000000",
        slug="test-tenant",
        name="Test Tenant",
        locale="ky-KG",
        timezone="Asia/Bishkek",
    )


def test_app_includes_openapi_and_auth_routes() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
    assert "/api/v1/auth/token" in response.json()["paths"]
    assert "/api/v1/auth/refresh" in response.json()["paths"]
    assert "/api/v1/auth/logout" in response.json()["paths"]
    assert "/api/v1/auth/register" in response.json()["paths"]


def test_auth_me_requires_authorization_header() -> None:
    app = create_app()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_tenant] = dummy_tenant
    client = TestClient(app)

    response = client.get("/api/v1/auth/me", headers={"X-Tenant-Slug": "test-tenant"})
    assert response.status_code == 401


def test_login_validates_request_payload() -> None:
    app = create_app()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_tenant] = dummy_tenant
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/token",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={"email": "invalid-email", "password": "short"},
    )
    assert response.status_code == 422
