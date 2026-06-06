from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.people import Student
from smart_school.models.school import School


async def get_school_by_id(
    session: AsyncSession, tenant_id: uuid.UUID, school_id: uuid.UUID
) -> School | None:
    result = await session.execute(select(School).filter_by(tenant_id=tenant_id, id=school_id))
    return result.scalar_one_or_none()


async def list_students(session: AsyncSession, tenant_id: uuid.UUID) -> list[Student]:
    result = await session.execute(select(Student).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def get_student_by_id(
    session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID
) -> Student | None:
    result = await session.execute(select(Student).filter_by(tenant_id=tenant_id, id=student_id))
    return result.scalar_one_or_none()


async def create_student(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    school_id: uuid.UUID,
    student_number: str,
    first_name: str,
    last_name: str,
    middle_name: str | None,
    date_of_birth: Any,
    gender: str,
    enrollment_date: Any,
    status: str = "active",
    profile: dict[str, Any] | None = None,
) -> Student:
    student = Student(
        tenant_id=tenant_id,
        school_id=school_id,
        student_number=student_number,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        date_of_birth=date_of_birth,
        gender=gender,
        status=status,
        enrollment_date=enrollment_date,
        profile=profile or {},
    )
    session.add(student)
    await session.flush()
    return student


async def update_student(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    student_number: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    middle_name: str | None = None,
    date_of_birth: Any | None = None,
    gender: str | None = None,
    status: str | None = None,
    enrollment_date: Any | None = None,
    profile: dict[str, Any] | None = None,
) -> Student | None:
    student = await get_student_by_id(session, tenant_id, student_id)
    if student is None:
        return None

    if student_number is not None:
        student.student_number = student_number
    if first_name is not None:
        student.first_name = first_name
    if last_name is not None:
        student.last_name = last_name
    if middle_name is not None:
        student.middle_name = middle_name
    if date_of_birth is not None:
        student.date_of_birth = date_of_birth
    if gender is not None:
        student.gender = gender
    if status is not None:
        student.status = status
    if enrollment_date is not None:
        student.enrollment_date = enrollment_date
    if profile is not None:
        student.profile = profile

    await session.flush()
    return student
