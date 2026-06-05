from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.attendance import AttendanceEvent, AttendanceMethod, AttendanceSession
from smart_school.models.people import Student
from smart_school.models.school import ClassGroup, School


async def get_school_by_id(session: AsyncSession, tenant_id: uuid.UUID, school_id: uuid.UUID) -> School | None:
    result = await session.execute(select(School).filter_by(tenant_id=tenant_id, id=school_id))
    return result.scalar_one_or_none()


async def get_class_group_by_id(session: AsyncSession, tenant_id: uuid.UUID, class_group_id: uuid.UUID) -> ClassGroup | None:
    result = await session.execute(select(ClassGroup).filter_by(tenant_id=tenant_id, id=class_group_id))
    return result.scalar_one_or_none()


async def get_session_by_id(session: AsyncSession, tenant_id: uuid.UUID, session_id: uuid.UUID) -> AttendanceSession | None:
    result = await session.execute(
        select(AttendanceSession).filter_by(tenant_id=tenant_id, id=session_id)
    )
    return result.scalar_one_or_none()


async def list_sessions(session: AsyncSession, tenant_id: uuid.UUID) -> list[AttendanceSession]:
    result = await session.execute(select(AttendanceSession).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def create_session(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    school_id: uuid.UUID,
    class_group_id: uuid.UUID,
    teacher_id: uuid.UUID | None,
    session_date: Any,
    period_code: str,
    starts_at: Any | None = None,
    ends_at: Any | None = None,
    status: str = "open",
) -> AttendanceSession:
    attendance_session = AttendanceSession(
        tenant_id=tenant_id,
        school_id=school_id,
        class_group_id=class_group_id,
        teacher_id=teacher_id,
        session_date=session_date,
        period_code=period_code,
        starts_at=starts_at,
        ends_at=ends_at,
        status=status,
    )
    session.add(attendance_session)
    await session.flush()
    return attendance_session


async def update_session(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    session_id: uuid.UUID,
    teacher_id: uuid.UUID | None = None,
    session_date: Any | None = None,
    period_code: str | None = None,
    starts_at: Any | None = None,
    ends_at: Any | None = None,
    status: str | None = None,
) -> AttendanceSession | None:
    attendance_session = await get_session_by_id(session, tenant_id, session_id)
    if attendance_session is None:
        return None

    if teacher_id is not None:
        attendance_session.teacher_id = teacher_id
    if session_date is not None:
        attendance_session.session_date = session_date
    if period_code is not None:
        attendance_session.period_code = period_code
    if starts_at is not None:
        attendance_session.starts_at = starts_at
    if ends_at is not None:
        attendance_session.ends_at = ends_at
    if status is not None:
        attendance_session.status = status

    await session.flush()
    return attendance_session


async def get_student_by_id(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> Student | None:
    result = await session.execute(select(Student).filter_by(tenant_id=tenant_id, id=student_id))
    return result.scalar_one_or_none()


async def list_events(session: AsyncSession, tenant_id: uuid.UUID, session_id: uuid.UUID | None = None) -> list[AttendanceEvent]:
    query = select(AttendanceEvent).filter_by(tenant_id=tenant_id)
    if session_id is not None:
        query = query.filter_by(session_id=session_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_event_by_id(session: AsyncSession, tenant_id: uuid.UUID, event_id: uuid.UUID) -> AttendanceEvent | None:
    result = await session.execute(
        select(AttendanceEvent).filter_by(tenant_id=tenant_id, id=event_id)
    )
    return result.scalar_one_or_none()


async def create_event(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    session_id: uuid.UUID,
    student_id: uuid.UUID,
    event_type: str,
    source: str,
    method: str,
    captured_at: Any,
    captured_by_user_id: uuid.UUID | None,
    idempotency_key: str,
    fraud_score: float | None = None,
    fraud_flags: dict[str, object] | None = None,
    confidence_score: float | None = None,
    evidence: dict[str, object] | None = None,
    notes: str | None = None,
) -> AttendanceEvent:
    attendance_event = AttendanceEvent(
        tenant_id=tenant_id,
        session_id=session_id,
        student_id=student_id,
        event_type=event_type,
        source=source,
        method=method,
        captured_at=captured_at,
        captured_by_user_id=captured_by_user_id,
        idempotency_key=idempotency_key,
        fraud_score=fraud_score,
        fraud_flags=fraud_flags or {},
        confidence_score=confidence_score,
        evidence=evidence or {},
        notes=notes,
    )
    session.add(attendance_event)
    try:
        await session.flush()
    except IntegrityError:
        raise
    return attendance_event
