from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

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
        email="teacher@example.com",
        first_name="Test",
        last_name="Teacher",
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


def test_app_includes_parent_routes() -> None:
    client = configure_test_app()

    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/parents/" in paths
    assert "/api/v1/parents/{parent_id}" in paths
    assert "/api/v1/parents/{parent_id}/students" in paths


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.parents.parents_crud.list_parent_profiles", new_callable=AsyncMock)
def test_list_parent_profiles_returns_profiles(
    mock_list_parent_profiles: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    parent_profile = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        phone_number="+996555123456",
        preferred_language="ky-KG",
        profile={"name": "Aida's mother"},
        ui_preferences={"mode": "simple", "contrast": "high"},
        created_at="2024-09-01T00:00:00",
        updated_at="2024-09-01T01:00:00",
    )
    mock_get_user_permissions.return_value = {"parents.read", "parents.manage"}
    mock_list_parent_profiles.return_value = [parent_profile]
    client = configure_test_app()

    response = client.get("/api/v1/parents", headers={"X-Tenant-Slug": "test-tenant"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(parent_profile.id),
            "user_id": str(parent_profile.user_id),
            "phone_number": "+996555123456",
            "preferred_language": "ky-KG",
            "profile": {"name": "Aida's mother"},
            "ui_preferences": {"mode": "simple", "contrast": "high"},
            "created_at": parent_profile.created_at,
            "updated_at": parent_profile.updated_at,
        }
    ]


@patch("smart_school.api.routers.parents.auth_crud.get_user_by_id", new_callable=AsyncMock)
@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.parents.parents_crud.create_parent_profile", new_callable=AsyncMock)
def test_create_parent_profile_validates_payload(
    mock_create_parent_profile: AsyncMock,
    mock_get_user_permissions: AsyncMock,
    mock_get_user_by_id: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"parents.manage", "parents.read"}
    mock_get_user_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000001"))
    mock_create_parent_profile.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        phone_number="+996555123456",
        preferred_language="ru-RU",
        profile={"notes": "Parent registered"},
        ui_preferences={"mode": "simple", "contrast": "high"},
        created_at="2024-09-01T00:00:00",
        updated_at="2024-09-01T00:00:00",
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/parents",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "user_id": str(mock_get_user_by_id.return_value.id),
            "phone_number": "+996555123456",
            "preferred_language": "ru-RU",
            "profile": {"notes": "Parent registered"},
            "ui_preferences": {"mode": "simple", "contrast": "high"},
        },
    )

    assert response.status_code == 201
    assert response.json()["phone_number"] == "+996555123456"
    assert response.json()["profile"] == {"notes": "Parent registered"}
    assert response.json()["ui_preferences"] == {"mode": "simple", "contrast": "high"}


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.parents.parents_crud.list_parent_student_links", new_callable=AsyncMock)
def test_list_parent_student_links_returns_links(
    mock_list_parent_student_links: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    link = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000030"),
        parent_profile_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        student_id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        relationship="mother",
        can_pick_up=True,
        emergency_contact=False,
        created_at="2024-09-01T00:00:00",
        updated_at="2024-09-01T00:00:00",
    )
    mock_get_user_permissions.return_value = {"parents.read", "parents.manage"}
    mock_list_parent_student_links.return_value = [link]
    client = configure_test_app()

    response = client.get(
        "/api/v1/parents/00000000-0000-0000-0000-000000000020/students",
        headers={"X-Tenant-Slug": "test-tenant"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(link.id),
            "parent_profile_id": str(link.parent_profile_id),
            "student_id": str(link.student_id),
            "relationship": "mother",
            "can_pick_up": True,
            "emergency_contact": False,
            "created_at": link.created_at,
            "updated_at": link.updated_at,
        }
    ]


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.parents.parents_crud.create_parent_student_link", new_callable=AsyncMock)
def test_create_parent_student_link_validates_payload(
    mock_create_parent_student_link: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"parents.manage", "parents.read"}
    mock_create_parent_student_link.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000040"),
        parent_profile_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        student_id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        relationship="father",
        can_pick_up=False,
        emergency_contact=True,
        created_at="2024-09-01T00:00:00",
        updated_at="2024-09-01T00:00:00",
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/parents/00000000-0000-0000-0000-000000000020/students",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "student_id": str(uuid.UUID("00000000-0000-0000-0000-000000000010")),
            "relationship": "father",
            "can_pick_up": False,
            "emergency_contact": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["relationship"] == "father"
    assert response.json()["emergency_contact"] is True
