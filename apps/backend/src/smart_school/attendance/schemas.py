from __future__ import annotations

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, constr


class AttendanceSessionCreateRequest(BaseModel):
    school_id: uuid.UUID
    class_group_id: uuid.UUID
    teacher_id: uuid.UUID | None = None
    session_date: date
    period_code: constr(min_length=1, max_length=40)
    starts_at: time | None = None
    ends_at: time | None = None
    status: str = Field(default="open")


class AttendanceSessionUpdateRequest(BaseModel):
    teacher_id: uuid.UUID | None = None
    session_date: date | None = None
    period_code: constr(min_length=1, max_length=40) | None = None
    starts_at: time | None = None
    ends_at: time | None = None
    status: str | None = None


class AttendanceSessionRead(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    class_group_id: uuid.UUID
    teacher_id: uuid.UUID | None
    session_date: date
    period_code: str
    starts_at: time | None
    ends_at: time | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceCaptureRequest(BaseModel):
    session_id: uuid.UUID
    student_id: uuid.UUID
    face_id_token: str | None = None
    qr_code_token: str | None = None
    nfc_tag: str | None = None
    manual_confirmation: bool | None = None
    source: str = Field(default="manual")
    captured_at: datetime
    captured_by_user_id: uuid.UUID | None = None
    idempotency_key: constr(min_length=1, max_length=120)
    confidence_score: float | None = None
    evidence: dict[str, object] = Field(default_factory=dict)
    notes: str | None = None


class AttendanceEventCreateRequest(BaseModel):
    session_id: uuid.UUID
    student_id: uuid.UUID
    event_type: str
    source: str
    method: str
    captured_at: datetime
    captured_by_user_id: uuid.UUID | None = None
    idempotency_key: constr(min_length=1, max_length=120)
    confidence_score: float | None = None
    evidence: dict[str, object] = Field(default_factory=dict)
    notes: str | None = None


class AttendanceEventRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    event_type: str
    source: str
    method: str
    captured_at: datetime
    captured_by_user_id: uuid.UUID | None
    idempotency_key: str
    fraud_score: float | None
    fraud_flags: dict[str, object]
    confidence_score: float | None
    evidence: dict[str, object]
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
