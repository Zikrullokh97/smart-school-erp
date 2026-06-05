from __future__ import annotations

import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth import crud as auth_crud
from smart_school.models.identity import User
from smart_school.models.people import Teacher
from smart_school.models.school import School


async def get_school_by_id(session: AsyncSession, tenant_id: uuid.UUID, school_id: uuid.UUID) -> School | None:
    result = await session.execute(
        select(School).filter_by(tenant_id=tenant_id, id=school_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> User | None:
    return await auth_crud.get_user_by_id(session, tenant_id, user_id)


async def list_teachers(session: AsyncSession, tenant_id: uuid.UUID) -> list[Teacher]:
    result = await session.execute(select(Teacher).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def get_teacher_by_id(session: AsyncSession, tenant_id: uuid.UUID, teacher_id: uuid.UUID) -> Teacher | None:
    result = await session.execute(
        select(Teacher).filter_by(tenant_id=tenant_id, id=teacher_id)
    )
    return result.scalar_one_or_none()


async def create_teacher(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    school_id: uuid.UUID,
    user_id: uuid.UUID | None,
    employee_number: str,
    first_name: str,
    last_name: str,
    hire_date: Any,
    status: str = "active",
    profile: dict[str, Any] | None = None,
) -> Teacher:
    teacher = Teacher(
        tenant_id=tenant_id,
        school_id=school_id,
        user_id=user_id,
        employee_number=employee_number,
        first_name=first_name,
        last_name=last_name,
        hire_date=hire_date,
        status=status,
        profile=profile or {},
    )
    session.add(teacher)
    await session.flush()
    return teacher


async def update_teacher(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    teacher_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    employee_number: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    hire_date: Any | None = None,
    status: str | None = None,
    profile: dict[str, Any] | None = None,
) -> Teacher | None:
    teacher = await get_teacher_by_id(session, tenant_id, teacher_id)
    if teacher is None:
        return None

    if user_id is not None:
        teacher.user_id = user_id
    if employee_number is not None:
        teacher.employee_number = employee_number
    if first_name is not None:
        teacher.first_name = first_name
    if last_name is not None:
        teacher.last_name = last_name
    if hire_date is not None:
        teacher.hire_date = hire_date
    if status is not None:
        teacher.status = status
    if profile is not None:
        teacher.profile = profile

    await session.flush()
    return teacher
