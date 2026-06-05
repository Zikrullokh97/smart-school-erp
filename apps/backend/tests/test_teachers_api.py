from __future__ import annotations

import uuid
from datetime import date, datetime
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


def test_app_includes_teacher_routes() -> None:
    client = configure_test_app()
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/teachers/" in paths
    assert "/api/v1/teachers/{teacher_id}" in paths


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.teachers.teachers_crud.list_teachers", new_callable=AsyncMock)
def test_list_teachers_returns_teachers(
    mock_list_teachers: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    teacher = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        school_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        employee_number="T1001",
        first_name="Aida",
        last_name="Ulanova",
        hire_date=date(2018, 9, 1),
        status="active",
        profile={},
        created_at=datetime(2024, 9, 1, 0, 0),
        updated_at=datetime(2024, 9, 1, 1, 0),
    )
    mock_get_user_permissions.return_value = {"teachers.read", "teachers.manage"}
    mock_list_teachers.return_value = [teacher]
    client = configure_test_app()

    response = client.get("/api/v1/teachers", headers={"X-Tenant-Slug": "test-tenant"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(teacher.id),
            "school_id": str(teacher.school_id),
            "user_id": str(teacher.user_id),
            "employee_number": "T1001",
            "first_name": "Aida",
            "last_name": "Ulanova",
            "hire_date": "2018-09-01",
            "status": "active",
            "profile": {},
            "created_at": teacher.created_at.isoformat(),
            "updated_at": teacher.updated_at.isoformat(),
        }
    ]


@patch("smart_school.api.routers.teachers.auth_crud.get_user_by_id", new_callable=AsyncMock)
@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.teachers.teachers_crud.get_school_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.teachers.teachers_crud.create_teacher", new_callable=AsyncMock)
def test_create_teacher_validates_payload(
    mock_create_teacher: AsyncMock,
    mock_get_school_by_id: AsyncMock,
    mock_get_user_permissions: AsyncMock,
    mock_get_user_by_id: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"teachers.manage", "teachers.read"}
    mock_get_school_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000020"))
    mock_get_user_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000001"))
    mock_create_teacher.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        school_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        employee_number="T1002",
        first_name="Erkin",
        last_name="Beyshenaliev",
        hire_date=date(2019, 9, 1),
        status="active",
        profile={"notes": "New teacher"},
        created_at=datetime(2024, 9, 1, 0, 0),
        updated_at=datetime(2024, 9, 1, 0, 0),
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/teachers",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "school_id": str(mock_get_school_by_id.return_value.id),
            "user_id": str(mock_get_user_by_id.return_value.id),
            "employee_number": "T1002",
            "first_name": "Erkin",
            "last_name": "Beyshenaliev",
            "hire_date": "2019-09-01",
            "profile": {"notes": "New teacher"},
        },
    )

    assert response.status_code == 201
    assert response.json()["employee_number"] == "T1002"
    assert response.json()["profile"] == {"notes": "New teacher"}
