from __future__ import annotations

import uuid
from datetime import date, datetime, time
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
        email="attendance@example.com",
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

        def add(self, obj: object) -> None:
            setattr(self, "last_added", obj)

    return DummySession()


def configure_test_app() -> TestClient:
    app = create_app()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_tenant] = dummy_tenant
    app.dependency_overrides[get_current_user] = dummy_user
    app.dependency_overrides[get_session] = lambda: dummy_session()
    return TestClient(app)


def test_app_includes_attendance_routes() -> None:
    client = configure_test_app()
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/attendance/sessions" in paths
    assert "/api/v1/attendance/events" in paths
    assert "/api/v1/attendance/capture" in paths


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.list_sessions", new_callable=AsyncMock)
def test_list_attendance_sessions_returns_sessions(
    mock_list_sessions: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    attendance_session = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        school_id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        class_group_id=uuid.UUID(int=0x30),
        teacher_id=uuid.UUID(int=0x1),
        session_date=date(2025, 1, 15),
        period_code="P1",
        starts_at=time(8, 0),
        ends_at=time(8, 45),
        status="open",
        created_at=datetime(2025, 1, 1, 9, 0),
        updated_at=datetime(2025, 1, 1, 9, 0),
    )
    mock_get_user_permissions.return_value = {"attendance.read"}
    mock_list_sessions.return_value = [attendance_session]
    client = configure_test_app()

    response = client.get("/api/v1/attendance/sessions", headers={"X-Tenant-Slug": "test-tenant"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(attendance_session.id),
            "school_id": str(attendance_session.school_id),
            "class_group_id": str(attendance_session.class_group_id),
            "teacher_id": str(attendance_session.teacher_id),
            "session_date": "2025-01-15",
            "period_code": "P1",
            "starts_at": "08:00:00",
            "ends_at": "08:45:00",
            "status": "open",
            "created_at": attendance_session.created_at.isoformat(),
            "updated_at": attendance_session.updated_at.isoformat(),
        }
    ]


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.get_school_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.get_class_group_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.create_session", new_callable=AsyncMock)
def test_create_attendance_session_validates_payload(
    mock_create_session: AsyncMock,
    mock_get_class_group_by_id: AsyncMock,
    mock_get_school_by_id: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"attendance.manage", "attendance.read"}
    mock_get_school_by_id.return_value = SimpleNamespace(id=uuid.UUID(int=0x20))
    mock_get_class_group_by_id.return_value = SimpleNamespace(id=uuid.UUID(int=0x30))
    mock_create_session.return_value = SimpleNamespace(
        id=uuid.UUID(int=0x40),
        school_id=uuid.UUID(int=0x20),
        class_group_id=uuid.UUID(int=0x30),
        teacher_id=uuid.UUID(int=0x1),
        session_date=date(2025, 2, 1),
        period_code="P2",
        starts_at=time(9, 0),
        ends_at=time(9, 45),
        status="open",
        created_at=datetime(2025, 2, 1, 8, 0),
        updated_at=datetime(2025, 2, 1, 8, 0),
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/attendance/sessions",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "school_id": str(mock_get_school_by_id.return_value.id),
            "class_group_id": str(mock_get_class_group_by_id.return_value.id),
            "teacher_id": str(mock_create_session.return_value.teacher_id),
            "session_date": "2025-02-01",
            "period_code": "P2",
            "starts_at": "09:00:00",
            "ends_at": "09:45:00",
        },
    )

    assert response.status_code == 201
    assert response.json()["period_code"] == "P2"
    assert response.json()["teacher_id"] == str(mock_create_session.return_value.teacher_id)


@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.get_session_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.get_student_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.create_event", new_callable=AsyncMock)
def test_create_attendance_event_validates_payload(
    mock_create_event: AsyncMock,
    mock_get_student_by_id: AsyncMock,
    mock_get_session_by_id: AsyncMock,
    mock_get_user_permissions: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"attendance.capture", "attendance.read"}
    mock_get_session_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000050"))
    mock_get_student_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000060"))
    mock_create_event.return_value = SimpleNamespace(
        id=uuid.UUID("00000000-0000-0000-0000-000000000070"),
        session_id=mock_get_session_by_id.return_value.id,
        student_id=mock_get_student_by_id.return_value.id,
        event_type="present",
        source="manual",
        method="manual",
        captured_at=datetime(2025, 2, 1, 9, 5, 0),
        captured_by_user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        idempotency_key="attendance-123",
        fraud_score=None,
        fraud_flags={},
        confidence_score=0.99,
        evidence={"device": "mobile"},
        notes="Arrived on time",
        created_at=datetime(2025, 2, 1, 9, 5, 0),
        updated_at=datetime(2025, 2, 1, 9, 5, 0),
    )
    client = configure_test_app()

    response = client.post(
        "/api/v1/attendance/events",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "session_id": str(mock_get_session_by_id.return_value.id),
            "student_id": str(mock_get_student_by_id.return_value.id),
            "event_type": "present",
            "source": "manual",
            "method": "manual",
            "captured_at": "2025-02-01T09:05:00",
            "idempotency_key": "attendance-123",
            "confidence_score": 0.99,
            "evidence": {"device": "mobile"},
            "notes": "Arrived on time",
        },
    )

    assert response.status_code == 201
    assert response.json()["event_type"] == "present"
    assert response.json()["idempotency_key"] == "attendance-123"


@patch("smart_school.api.routers.attendance.attendance_crud.get_session_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_crud.get_student_by_id", new_callable=AsyncMock)
@patch("smart_school.api.routers.attendance.attendance_services.capture_attendance_event", new_callable=AsyncMock)
@patch("smart_school.auth.dependencies.get_user_permissions", new_callable=AsyncMock)
def test_capture_attendance_event_falls_back_and_returns_event(
    mock_get_user_permissions: AsyncMock,
    mock_capture_event: AsyncMock,
    mock_get_student_by_id: AsyncMock,
    mock_get_session_by_id: AsyncMock,
) -> None:
    mock_get_user_permissions.return_value = {"attendance.capture", "attendance.read"}
    mock_get_session_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000050"))
    mock_get_student_by_id.return_value = SimpleNamespace(id=uuid.UUID("00000000-0000-0000-0000-000000000060"))
    mock_capture_event.return_value = (
        SimpleNamespace(
            id=uuid.UUID("00000000-0000-0000-0000-000000000080"),
            session_id=mock_get_session_by_id.return_value.id,
            student_id=mock_get_student_by_id.return_value.id,
            event_type="present",
            source="face_id",
            method="face_id",
            captured_at=datetime(2025, 2, 1, 9, 10, 0),
            captured_by_user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            idempotency_key="attendance-capture-123",
            fraud_score=0.0,
            fraud_flags={},
            confidence_score=0.98,
            evidence={"fallback_path": ["face_id"], "requested_source": "manual"},
            notes="Captured via fallback",
            created_at=datetime(2025, 2, 1, 9, 10, 0),
            updated_at=datetime(2025, 2, 1, 9, 10, 0),
        ),
        SimpleNamespace(
            method=SimpleNamespace(value="face_id"),
            source=SimpleNamespace(value="face_id"),
            fraud_score=None,
            fraud_flags={},
            evidence={"fallback_path": ["face_id"], "requested_source": "manual"},
        ),
    )

    client = configure_test_app()
    response = client.post(
        "/api/v1/attendance/capture",
        headers={"X-Tenant-Slug": "test-tenant"},
        json={
            "session_id": str(mock_get_session_by_id.return_value.id),
            "student_id": str(mock_get_student_by_id.return_value.id),
            "face_id_token": "token-abc",
            "source": "manual",
            "captured_at": "2025-02-01T09:10:00",
            "idempotency_key": "attendance-capture-123",
            "confidence_score": 0.98,
            "notes": "Captured via fallback",
        },
    )

    assert response.status_code == 201
    assert response.json()["source"] == "face_id"
    assert response.json()["method"] == "face_id"
    assert response.json()["idempotency_key"] == "attendance-capture-123"
