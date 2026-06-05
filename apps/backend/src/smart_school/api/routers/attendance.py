from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.dependencies import (
    get_current_tenant,
    get_current_user,
    get_session,
    require_permission,
)
from smart_school.attendance import crud as attendance_crud
from smart_school.attendance import services as attendance_services
from smart_school.attendance.schemas import (
    AttendanceCaptureRequest,
    AttendanceEventCreateRequest,
    AttendanceEventRead,
    AttendanceSessionCreateRequest,
    AttendanceSessionRead,
    AttendanceSessionUpdateRequest,
)
from smart_school.models.audit import AuditLog
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/sessions", response_model=list[AttendanceSessionRead])
async def list_attendance_sessions(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.read")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[AttendanceSessionRead]:
    sessions = await attendance_crud.list_sessions(session, tenant.id)
    return [AttendanceSessionRead.model_validate(item) for item in sessions]


@router.get("/sessions/{session_id}", response_model=AttendanceSessionRead)
async def read_attendance_session(
    session_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.read")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceSessionRead:
    attendance_session = await attendance_crud.get_session_by_id(session, tenant.id, session_id)
    if attendance_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance session not found.")
    return AttendanceSessionRead.model_validate(attendance_session)


@router.post("/sessions", response_model=AttendanceSessionRead, status_code=status.HTTP_201_CREATED)
async def create_attendance_session(
    payload: AttendanceSessionCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.manage")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceSessionRead:
    school = await attendance_crud.get_school_by_id(session, tenant.id, payload.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found.")

    class_group = await attendance_crud.get_class_group_by_id(session, tenant.id, payload.class_group_id)
    if class_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class group not found.")

    attendance_session = await attendance_crud.create_session(
        session,
        tenant.id,
        payload.school_id,
        payload.class_group_id,
        payload.teacher_id,
        payload.session_date,
        payload.period_code,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        status=payload.status,
    )
    await session.commit()
    return AttendanceSessionRead.model_validate(attendance_session)


@router.patch("/sessions/{session_id}", response_model=AttendanceSessionRead)
async def update_attendance_session(
    session_id: uuid.UUID,
    payload: AttendanceSessionUpdateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.manage")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceSessionRead:
    attendance_session = await attendance_crud.update_session(
        session,
        tenant.id,
        session_id,
        teacher_id=payload.teacher_id,
        session_date=payload.session_date,
        period_code=payload.period_code,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        status=payload.status,
    )
    if attendance_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance session not found.")
    await session.commit()
    return AttendanceSessionRead.model_validate(attendance_session)


@router.get("/events", response_model=list[AttendanceEventRead])
async def list_attendance_events(
    session_id: Annotated[uuid.UUID | None, Query(alias="session_id")] = None,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.read")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[AttendanceEventRead]:
    events = await attendance_crud.list_events(session, tenant.id, session_id)
    return [AttendanceEventRead.model_validate(item) for item in events]


@router.get("/events/{event_id}", response_model=AttendanceEventRead)
async def read_attendance_event(
    event_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.read")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceEventRead:
    event = await attendance_crud.get_event_by_id(session, tenant.id, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance event not found.")
    return AttendanceEventRead.model_validate(event)


@router.post("/capture", response_model=AttendanceEventRead, status_code=status.HTTP_201_CREATED)
async def capture_attendance(
    payload: AttendanceCaptureRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    user=Depends(require_permission("attendance.capture")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceEventRead:
    attendance_session = await attendance_crud.get_session_by_id(session, tenant.id, payload.session_id)
    if attendance_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance session not found.")

    student = await attendance_crud.get_student_by_id(session, tenant.id, payload.student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    try:
        attendance_event, capture_result = await attendance_services.capture_attendance_event(
            session,
            tenant.id,
            payload.session_id,
            payload.student_id,
            "present",
            payload.face_id_token,
            payload.qr_code_token,
            payload.nfc_tag,
            payload.manual_confirmation,
            payload.source,
            payload.captured_at,
            payload.captured_by_user_id,
            payload.idempotency_key,
            payload.confidence_score,
            payload.notes,
        )
        audit_entry = AuditLog(
            tenant_id=tenant.id,
            actor_user_id=user.id,
            action="attendance.capture",
            target_type="AttendanceEvent",
            target_id=attendance_event.id,
            summary={
                "method": capture_result.method.value,
                "source": capture_result.source.value,
                "fraud_flags": capture_result.fraud_flags,
            },
        )
        session.add(audit_entry)
        await session.commit()
        return AttendanceEventRead.model_validate(attendance_event)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance event with this idempotency key already exists.",
        ) from exc


@router.post("/events", response_model=AttendanceEventRead, status_code=status.HTTP_201_CREATED)
async def create_attendance_event(
    payload: AttendanceEventCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user=Depends(require_permission("attendance.capture")),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttendanceEventRead:
    attendance_session = await attendance_crud.get_session_by_id(session, tenant.id, payload.session_id)
    if attendance_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance session not found.")

    student = await attendance_crud.get_student_by_id(session, tenant.id, payload.student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    try:
        attendance_event = await attendance_crud.create_event(
            session,
            tenant.id,
            payload.session_id,
            payload.student_id,
            payload.event_type,
            payload.source,
            payload.method,
            payload.captured_at,
            payload.captured_by_user_id,
            payload.idempotency_key,
            confidence_score=payload.confidence_score,
            evidence=payload.evidence,
            notes=payload.notes,
        )
        await session.commit()
        return AttendanceEventRead.model_validate(attendance_event)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance event with this idempotency key already exists.",
        ) from exc
