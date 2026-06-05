from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class SyncDeviceCreateRequest(BaseModel):
    device_key: constr(min_length=1, max_length=160)
    platform: constr(min_length=1, max_length=40)
    app_version: constr(min_length=1, max_length=40)


class SyncDeviceRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    device_key: str
    platform: str
    app_version: str
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncOperationCreateRequest(BaseModel):
    device_id: uuid.UUID
    operation_id: constr(min_length=1, max_length=160)
    resource_type: constr(min_length=1, max_length=120)
    resource_id: uuid.UUID | None = None
    operation_type: constr(min_length=1, max_length=80)
    payload_version: int = Field(gt=0)
    payload: dict[str, object]
    base_revision: str | None = None


class SyncOperationRead(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    user_id: uuid.UUID
    operation_id: str
    resource_type: str
    resource_id: uuid.UUID | None
    operation_type: str
    payload_version: int
    payload: dict[str, object]
    base_revision: str | None
    status: str
    conflict_details: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncOperationResolveRequest(BaseModel):
    resolution: constr(min_length=1, max_length=40)
    details: dict[str, object] = Field(default_factory=dict)
