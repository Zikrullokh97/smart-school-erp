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


def test_app_includes_student_routes() -> None:
    client = configure_test_app()

    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/students/" in paths
    assert "/api/v1/students/{student_id}" in paths


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.students.students_crud.list_students", new_callable=AsyncMock)
def test_list_students_returns_students(
    mock_list_students: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    student = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        school_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        student_number="S1001",
        first_name="Aida",
        last_name="Ulanova",
        middle_name=None,
        date_of_birth=date(2012, 6, 14),
        gender="female",
        status="active",
        enrollment_date=date(2024, 9, 1),
        profile={},
        created_at=datetime(2024, 9, 1, 0, 0),
        updated_at=datetime(2024, 9, 1, 1, 0),
    )
    mock_get_user_permissions.return_value = {"students.read", "students.manage"}
    mock_list_students.return_value = [student]
    client = configure_test_app()

    response = client.get("/api/v1/students", headers={"X-Tenant-Slug": "test-tenant"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(student.id),
            "school_id": str(student.school_id),
            "student_number": "S1001",
            "first_name": "Aida",
            "last_name": "Ulanova",
            "middle_name": None,
            "date_of_birth": "2012-06-14",
            "gender": "female",
            "status": "active",
            "enrollment_date": "2024-09-01",
            "profile": {},
            "created_at": student.created_at.isoformat(),
            "updated_at": student.updated_at.isoformat(),
        }
    ]


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.students.students_crud.get_school_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.students.students_crud.create_student", new_callable=AsyncMock)
def test_create_student_validates_payload(
    mock_create_student: AsyncMock,
    mock_get_school_by_id: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"students.manage", "students.read"}
    mock_get_school_by_id.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000020")
    )
    mock_create_student.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        school_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        student_number="S1002",
        first_name="Erkin",
        last_name="Beyshenaliev",
        middle_name="A",
        date_of_birth=date(2011, 8, 20),
        gender="male",
        status="active",
        enrollment_date=date(2024, 9, 1),
        profile={"notes": "New student"},
        created_at=datetime(2024, 9, 1, 0, 0),
        updated_at=datetime(2024, 9, 1, 0, 0),
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/students",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "school_id": str(mock_get_school_by_id.return_value.id),
            "student_number": "S1002",
            "first_name": "Erkin",
            "last_name": "Beyshenaliev",
            "middle_name": "A",
            "date_of_birth": "2011-08-20",
            "gender": "male",
            "enrollment_date": "2024-09-01",
            "profile": {"notes": "New student"},
        },
    )

    assert response.status_code == 201
    assert response.json()["student_number"] == "S1002"
    assert response.json()["profile"] == {"notes": "New student"}
