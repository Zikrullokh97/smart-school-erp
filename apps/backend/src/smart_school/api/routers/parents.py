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
from smart_school.parents import crud as parents_crud
from smart_school.parents.schemas import (
    ParentProfileCreateRequest,
    ParentProfileRead,
    ParentProfileUpdateRequest,
    ParentStudentLinkCreateRequest,
    ParentStudentLinkRead,
)

router = APIRouter(prefix="/parents", tags=["Parents"])
parents_read_permission = require_permission("parents.read")
parents_manage_permission = require_permission("parents.manage")


@router.get("/", response_model=list[ParentProfileRead])
async def list_parent_profiles(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[ParentProfileRead]:
    parents = await parents_crud.list_parent_profiles(session, tenant.id)
    return [ParentProfileRead.model_validate(parent) for parent in parents]


@router.get("/{parent_id}", response_model=ParentProfileRead)
async def read_parent_profile(
    parent_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ParentProfileRead:
    parent_profile = await parents_crud.get_parent_profile_by_id(session, tenant.id, parent_id)
    if parent_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found."
        )
    return ParentProfileRead.model_validate(parent_profile)


@router.post("/", response_model=ParentProfileRead, status_code=status.HTTP_201_CREATED)
async def create_parent_profile(
    payload: ParentProfileCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ParentProfileRead:
    if payload.user_id is not None:
        user = await auth_crud.get_user_by_id(session, tenant.id, payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    parent = await parents_crud.create_parent_profile(
        session,
        tenant.id,
        payload.user_id,
        payload.phone_number,
        payload.preferred_language,
        profile=payload.profile,
        ui_preferences=payload.ui_preferences,
    )
    await session.commit()
    return ParentProfileRead.model_validate(parent)


@router.patch("/{parent_id}", response_model=ParentProfileRead)
async def update_parent_profile(
    parent_id: uuid.UUID,
    payload: ParentProfileUpdateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ParentProfileRead:
    if payload.user_id is not None:
        user = await auth_crud.get_user_by_id(session, tenant.id, payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    parent = await parents_crud.update_parent_profile(
        session,
        tenant.id,
        parent_id,
        user_id=payload.user_id,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language,
        profile=payload.profile,
        ui_preferences=payload.ui_preferences,
    )
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found."
        )
    await session.commit()
    return ParentProfileRead.model_validate(parent)


@router.get("/{parent_id}/students", response_model=list[ParentStudentLinkRead])
async def list_parent_student_links(
    parent_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[ParentStudentLinkRead]:
    links = await parents_crud.list_parent_student_links(session, tenant.id, parent_id)
    return [ParentStudentLinkRead.model_validate(link) for link in links]


@router.post(
    "/{parent_id}/students",
    response_model=ParentStudentLinkRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_parent_student_link(
    parent_id: uuid.UUID,
    payload: ParentStudentLinkCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> ParentStudentLinkRead:
    try:
        link = await parents_crud.create_parent_student_link(
            session,
            tenant.id,
            parent_id,
            payload.student_id,
            payload.relationship,
            payload.can_pick_up,
            payload.emergency_contact,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return ParentStudentLinkRead.model_validate(link)


@router.delete("/{parent_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent_student_link(
    parent_id: uuid.UUID,
    student_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(parents_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> None:
    removed = await parents_crud.delete_parent_student_link(
        session, tenant.id, parent_id, student_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent student link not found."
        )
    await session.commit()
