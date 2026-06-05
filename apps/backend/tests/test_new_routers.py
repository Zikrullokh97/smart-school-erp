from __future__ import annotations

import uuid
from types import SimpleNamespace
from fastapi.testclient import TestClient

from smart_school.app import create_app
from smart_school.auth.dependencies import get_current_tenant, get_current_user, get_session


def dummy_tenant() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        slug="test-tenant",
        name="Test Tenant",
        locale="ky-KG",
        timezone="Asia/Bishkek",
    )


def dummy_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        email="user@example.com",
        first_name="Test",
        last_name="User",
        status="active",
        locale="ky-KG",
        roles=[],
    )


def dummy_session() -> SimpleNamespace:
    class DummySession(SimpleNamespace):
        async def commit(self) -> None:
            pass

    return DummySession()


def configure_test_app() -> TestClient:
    app = create_app()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_tenant] = dummy_tenant
    app.dependency_overrides[get_current_user] = dummy_user
    app.dependency_overrides[get_session] = lambda: dummy_session()
    return TestClient(app)


def test_new_routers_are_registered() -> None:
    client = configure_test_app()

    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]

    assert "/api/v1/students/{student_id}/gamification" in paths
    assert "/api/v1/ai/reports/queue" in paths
    assert "/api/v1/sync/devices" in paths
