from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth import crud as auth_crud
from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.auth.schemas import UserCreateRequest, UserRead, UserUpdateRequest
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/users", tags=["Users"])
users_read_permission = require_permission("users.read")
users_manage_permission = require_permission("users.manage")


@router.get("/", response_model=list[UserRead])
async def list_users(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(users_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[UserRead]:
    result = await session.execute(select(User).filter_by(tenant_id=tenant.id))
    users = result.scalars().all()
    return [
        UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            locale=user.locale,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role_codes=[role.code for role in user.roles],
        )
        for user in users
    ]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(users_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> UserRead:
    user = await auth_crud.create_user(
        session,
        tenant.id,
        payload.email,
        payload.password,
        payload.first_name,
        payload.last_name,
        status=payload.status,
        locale=payload.locale,
        role_codes=payload.role_codes,
    )
    await session.commit()
    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status=user.status,
        locale=user.locale,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_codes=payload.role_codes,
    )


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(users_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> UserRead:
    user = await auth_crud.get_user_by_id(session, tenant.id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.locale is not None:
        user.locale = payload.locale
    if payload.status is not None:
        user.status = payload.status
    await session.flush()
    await session.commit()
    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status=user.status,
        locale=user.locale,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_codes=[role.code for role in user.roles],
    )
