from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class ParentProfileCreateRequest(BaseModel):
    user_id: uuid.UUID | None = None
    phone_number: constr(min_length=1, max_length=40)
    preferred_language: constr(min_length=2, max_length=16) = Field(default="ky-KG")
    profile: dict[str, object] = Field(default_factory=dict)
    ui_preferences: dict[str, object] = Field(default_factory=dict)


class ParentProfileUpdateRequest(BaseModel):
    user_id: uuid.UUID | None = None
    phone_number: constr(min_length=1, max_length=40) | None = None
    preferred_language: constr(min_length=2, max_length=16) | None = None
    profile: dict[str, object] | None = None
    ui_preferences: dict[str, object] | None = None


class ParentProfileRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    phone_number: str
    preferred_language: str
    profile: dict[str, object]
    ui_preferences: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParentStudentLinkCreateRequest(BaseModel):
    student_id: uuid.UUID
    relationship: constr(min_length=1, max_length=80)
    can_pick_up: bool = False
    emergency_contact: bool = False


class ParentStudentLinkRead(BaseModel):
    id: uuid.UUID
    parent_profile_id: uuid.UUID
    student_id: uuid.UUID
    relationship: str
    can_pick_up: bool
    emergency_contact: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
