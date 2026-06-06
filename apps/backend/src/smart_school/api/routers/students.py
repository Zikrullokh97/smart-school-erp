from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant
from smart_school.students import crud as students_crud
from smart_school.students.schemas import (
    StudentCreateRequest,
    StudentRead,
    StudentUpdateRequest,
)

router = APIRouter(prefix="/students", tags=["Students"])
students_read_permission = require_permission("students.read")
students_manage_permission = require_permission("students.manage")


@router.get("/", response_model=list[StudentRead])
async def list_students(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[StudentRead]:
    students = await students_crud.list_students(session, tenant.id)
    return [StudentRead.model_validate(student) for student in students]


@router.get("/{student_id}", response_model=StudentRead)
async def read_student(
    student_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> StudentRead:
    student = await students_crud.get_student_by_id(session, tenant.id, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return StudentRead.model_validate(student)


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> StudentRead:
    school = await students_crud.get_school_by_id(session, tenant.id, payload.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found.")

    student = await students_crud.create_student(
        session,
        tenant.id,
        payload.school_id,
        payload.student_number,
        payload.first_name,
        payload.last_name,
        payload.middle_name,
        payload.date_of_birth,
        payload.gender,
        payload.enrollment_date,
        status=payload.status,
        profile=payload.profile,
    )
    await session.commit()
    return StudentRead.model_validate(student)


@router.patch("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> StudentRead:
    student = await students_crud.update_student(
        session,
        tenant.id,
        student_id,
        student_number=payload.student_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        status=payload.status,
        enrollment_date=payload.enrollment_date,
        profile=payload.profile,
    )
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    await session.commit()
    return StudentRead.model_validate(student)
