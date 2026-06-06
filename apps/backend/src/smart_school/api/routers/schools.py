from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth import crud as auth_crud
from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.auth.schemas import SchoolCreateRequest, SchoolRead
from smart_school.models.identity import User
from smart_school.models.school import School
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/schools", tags=["Schools"])
schools_read_permission = require_permission("schools.read")
schools_manage_permission = require_permission("schools.manage")


@router.get("/", response_model=list[SchoolRead])
async def list_schools(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(schools_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[SchoolRead]:
    result = await session.execute(select(School).filter_by(tenant_id=tenant.id))
    schools = result.scalars().all()
    return [SchoolRead.model_validate(school) for school in schools]


@router.post("/", response_model=SchoolRead, status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: SchoolCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(schools_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> SchoolRead:
    school = await auth_crud.create_school(
        session,
        tenant.id,
        payload.name,
        payload.code,
        payload.region,
        payload.district,
        payload.address,
        payload.timezone,
        payload.language_code,
    )
    await session.commit()
    return SchoolRead.model_validate(school)
