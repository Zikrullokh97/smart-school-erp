from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.sync import SyncDevice, SyncOperation
from smart_school.models.enums import SyncOperationStatus


async def create_sync_device(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    device_key: str,
    platform: str,
    app_version: str,
) -> SyncDevice:
    device = SyncDevice(
        tenant_id=tenant_id,
        user_id=user_id,
        device_key=device_key,
        platform=platform,
        app_version=app_version,
    )
    session.add(device)
    await session.flush()
    return device


async def get_sync_device_by_id(session: AsyncSession, tenant_id: uuid.UUID, device_id: uuid.UUID) -> SyncDevice | None:
    result = await session.execute(select(SyncDevice).filter_by(tenant_id=tenant_id, id=device_id))
    return result.scalar_one_or_none()


async def list_sync_devices(session: AsyncSession, tenant_id: uuid.UUID) -> list[SyncDevice]:
    result = await session.execute(select(SyncDevice).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def create_sync_operation(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    device_id: uuid.UUID,
    operation_id: str,
    resource_type: str,
    resource_id: uuid.UUID | None,
    operation_type: str,
    payload_version: int,
    payload: dict[str, object],
    base_revision: str | None,
) -> SyncOperation:
    operation = SyncOperation(
        tenant_id=tenant_id,
        user_id=user_id,
        device_id=device_id,
        operation_id=operation_id,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_type=operation_type,
        payload_version=payload_version,
        payload=payload,
        base_revision=base_revision,
    )
    session.add(operation)
    await session.flush()
    return operation


async def list_sync_operations(session: AsyncSession, tenant_id: uuid.UUID) -> list[SyncOperation]:
    result = await session.execute(select(SyncOperation).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def get_sync_operation_by_id(session: AsyncSession, tenant_id: uuid.UUID, operation_id: uuid.UUID) -> SyncOperation | None:
    result = await session.execute(select(SyncOperation).filter_by(tenant_id=tenant_id, id=operation_id))
    return result.scalar_one_or_none()


async def resolve_sync_operation(
    session: AsyncSession,
    operation: SyncOperation,
    resolution: str,
    details: dict[str, object],
) -> SyncOperation:
    if resolution == "apply":
        operation.status = SyncOperationStatus.APPLIED
    elif resolution == "reject":
        operation.status = SyncOperationStatus.REJECTED
    else:
        operation.status = SyncOperationStatus.CONFLICTED
    operation.conflict_details = details
    await session.flush()
    return operation
