from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class TeacherCreateRequest(BaseModel):
    school_id: uuid.UUID
    user_id: uuid.UUID | None = None
    employee_number: constr(min_length=1, max_length=80)
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    hire_date: date
    status: str = Field(default="active")
    profile: dict[str, object] = Field(default_factory=dict)


class TeacherUpdateRequest(BaseModel):
    user_id: uuid.UUID | None = None
    employee_number: constr(min_length=1, max_length=80) | None = None
    first_name: constr(min_length=1, max_length=120) | None = None
    last_name: constr(min_length=1, max_length=120) | None = None
    hire_date: date | None = None
    status: str | None = None
    profile: dict[str, object] | None = None


class TeacherRead(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    user_id: uuid.UUID | None
    employee_number: str
    first_name: str
    last_name: str
    hire_date: date
    status: str
    profile: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
