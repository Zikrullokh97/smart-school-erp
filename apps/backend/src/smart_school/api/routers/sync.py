from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant
from smart_school.sync import crud as sync_crud
from smart_school.sync.schemas import (
    SyncDeviceCreateRequest,
    SyncDeviceRead,
    SyncOperationCreateRequest,
    SyncOperationRead,
    SyncOperationResolveRequest,
)

router = APIRouter(prefix="/sync", tags=["Sync"])
sync_manage_permission = require_permission("sync.manage")


@router.post("/devices", response_model=SyncDeviceRead, status_code=status.HTTP_201_CREATED)
async def register_sync_device(
    payload: SyncDeviceCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    user: Annotated[User, Depends(sync_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> SyncDeviceRead:
    device = await sync_crud.create_sync_device(
        session,
        tenant.id,
        user.id,
        payload.device_key,
        payload.platform,
        payload.app_version,
    )
    await session.commit()
    return SyncDeviceRead.model_validate(device)


@router.get("/devices", response_model=list[SyncDeviceRead])
async def list_sync_devices(
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(sync_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[SyncDeviceRead]:
    devices = await sync_crud.list_sync_devices(session, tenant.id)
    return [SyncDeviceRead.model_validate(device) for device in devices]


@router.post("/operations", response_model=SyncOperationRead, status_code=status.HTTP_201_CREATED)
async def submit_sync_operation(
    payload: SyncOperationCreateRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    user: Annotated[User, Depends(sync_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> SyncOperationRead:
    device = await sync_crud.get_sync_device_by_id(session, tenant.id, payload.device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync device not found.")

    operation = await sync_crud.create_sync_operation(
        session,
        tenant.id,
        user.id,
        payload.device_id,
        payload.operation_id,
        payload.resource_type,
        payload.resource_id,
        payload.operation_type,
        payload.payload_version,
        payload.payload,
        payload.base_revision,
    )
    await session.commit()
    return SyncOperationRead.model_validate(operation)


@router.get("/operations", response_model=list[SyncOperationRead])
async def list_sync_operations(
    status: str | None = Query(default=None),
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(sync_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[SyncOperationRead]:
    operations = await sync_crud.list_sync_operations(session, tenant.id)
    if status is not None:
        operations = [op for op in operations if op.status.value == status]
    return [SyncOperationRead.model_validate(operation) for operation in operations]


@router.post("/operations/{operation_id}/resolve", response_model=SyncOperationRead)
async def resolve_sync_operation(
    operation_id: uuid.UUID,
    payload: SyncOperationResolveRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    user: Annotated[User, Depends(sync_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> SyncOperationRead:
    operation = await sync_crud.get_sync_operation_by_id(session, tenant.id, operation_id)
    if operation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sync operation not found."
        )

    resolved = await sync_crud.resolve_sync_operation(
        session, operation, payload.resolution, payload.details
    )
    await session.commit()
    return SyncOperationRead.model_validate(resolved)
