from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, constr


class StudentCreateRequest(BaseModel):
    school_id: uuid.UUID
    student_number: constr(min_length=1, max_length=80)
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    middle_name: constr(min_length=1, max_length=120) | None = None
    date_of_birth: date
    gender: constr(min_length=1, max_length=32)
    enrollment_date: date
    status: str = Field(default="active")
    profile: dict[str, object] = Field(default_factory=dict)


class StudentUpdateRequest(BaseModel):
    student_number: constr(min_length=1, max_length=80) | None = None
    first_name: constr(min_length=1, max_length=120) | None = None
    last_name: constr(min_length=1, max_length=120) | None = None
    middle_name: constr(min_length=1, max_length=120) | None = None
    date_of_birth: date | None = None
    gender: constr(min_length=1, max_length=32) | None = None
    enrollment_date: date | None = None
    status: str | None = None
    profile: dict[str, object] | None = None


class StudentRead(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    student_number: str
    first_name: str
    last_name: str
    middle_name: str | None
    date_of_birth: date
    gender: str
    status: str
    enrollment_date: date
    profile: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
