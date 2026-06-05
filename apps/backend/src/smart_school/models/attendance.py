from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Time, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import (
    AttendanceEventType,
    AttendanceSessionStatus,
    AttendanceSource,
    AttendanceMethod,
    BiometricStatus,
)
from smart_school.models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AttendanceSession(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "class_group_id",
            "session_date",
            "period_code",
            name="uq_attendance_sessions_period",
        ),
    )

    school_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    class_group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("class_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_code: Mapped[str] = mapped_column(String(40), nullable=False)
    starts_at: Mapped[time | None] = mapped_column(Time(timezone=True), nullable=True)
    ends_at: Mapped[time | None] = mapped_column(Time(timezone=True), nullable=True)
    status: Mapped[AttendanceSessionStatus] = mapped_column(
        enum_type(AttendanceSessionStatus, "attendance_session_status"),
        nullable=False,
        default=AttendanceSessionStatus.OPEN,
        server_default=AttendanceSessionStatus.OPEN.value,
    )


class AttendanceEvent(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "attendance_events"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_attendance_events_idempotency"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[AttendanceEventType] = mapped_column(
        enum_type(AttendanceEventType, "attendance_event_type"),
        nullable=False,
    )
    source: Mapped[AttendanceSource] = mapped_column(
        enum_type(AttendanceSource, "attendance_source"),
        nullable=False,
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        enum_type(AttendanceMethod, "attendance_method"),
        nullable=False,
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    captured_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    fraud_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    fraud_flags: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class FaceEmbedding(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "face_embeddings"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "student_id",
            "model_name",
            "model_version",
            name="uq_face_embeddings_student_model",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    consent_reference: Mapped[str] = mapped_column(String(160), nullable=False)
    consent_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[BiometricStatus] = mapped_column(
        enum_type(BiometricStatus, "biometric_status"),
        nullable=False,
        default=BiometricStatus.ACTIVE,
        server_default=BiometricStatus.ACTIVE.value,
    )
