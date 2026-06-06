from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth import crud as auth_crud
from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant
from smart_school.teachers import crud as teachers_crud
from smart_school.teachers.schemas import (
    TeacherCreateRequest,
    TeacherRead,
    TeacherUpdateRequest,
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])
teachers_read_permission = require_permission("teachers.read")
teachers_manage_permission = require_permission("teachers.manage")


@router.get("/", response_model=list[TeacherRead])
async def list_teachers(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(teachers_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[TeacherRead]:
    teachers = await teachers_crud.list_teachers(session, tenant.id)
    return [TeacherRead.model_validate(teacher) for teacher in teachers]


@router.get("/{teacher_id}", response_model=TeacherRead)
async def read_teacher(
    teacher_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(teachers_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TeacherRead:
    teacher = await teachers_crud.get_teacher_by_id(session, tenant.id, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")
    return TeacherRead.model_validate(teacher)


@router.post("/", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    payload: TeacherCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(teachers_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TeacherRead:
    school = await teachers_crud.get_school_by_id(session, tenant.id, payload.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found.")

    if payload.user_id is not None:
        user = await auth_crud.get_user_by_id(session, tenant.id, payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    teacher = await teachers_crud.create_teacher(
        session,
        tenant.id,
        payload.school_id,
        payload.user_id,
        payload.employee_number,
        payload.first_name,
        payload.last_name,
        payload.hire_date,
        status=payload.status,
        profile=payload.profile,
    )
    await session.commit()
    return TeacherRead.model_validate(teacher)


@router.patch("/{teacher_id}", response_model=TeacherRead)
async def update_teacher(
    teacher_id: uuid.UUID,
    payload: TeacherUpdateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(teachers_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TeacherRead:
    if payload.user_id is not None:
        user = await auth_crud.get_user_by_id(session, tenant.id, payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    teacher = await teachers_crud.update_teacher(
        session,
        tenant.id,
        teacher_id,
        user_id=payload.user_id,
        employee_number=payload.employee_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        hire_date=payload.hire_date,
        status=payload.status,
        profile=payload.profile,
    )
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")
    await session.commit()
    return TeacherRead.model_validate(teacher)
