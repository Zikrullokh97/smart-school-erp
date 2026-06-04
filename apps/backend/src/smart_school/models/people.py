from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import PersonStatus
from smart_school.models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Student(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("tenant_id", "school_id", "student_number", name="uq_students_number"),
    )

    school_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_number: Mapped[str] = mapped_column(String(80), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[PersonStatus] = mapped_column(
        enum_type(PersonStatus, "person_status"),
        nullable=False,
        default=PersonStatus.ACTIVE,
        server_default=PersonStatus.ACTIVE.value,
    )
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class Teacher(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "teachers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "school_id", "employee_number", name="uq_teachers_number"),
    )

    school_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employee_number: Mapped[str] = mapped_column(String(80), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PersonStatus] = mapped_column(
        enum_type(PersonStatus, "teacher_status"),
        nullable=False,
        default=PersonStatus.ACTIVE,
        server_default=PersonStatus.ACTIVE.value,
    )
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class ParentProfile(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "parent_profiles"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_parent_profiles_user"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(16), nullable=False, default="ky-KG")
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class ParentStudentLink(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "parent_student_links"
    __table_args__ = (
        UniqueConstraint("tenant_id", "parent_profile_id", "student_id", name="uq_parent_student"),
    )

    parent_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("parent_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship: Mapped[str] = mapped_column(String(80), nullable=False)
    can_pick_up: Mapped[bool] = mapped_column(nullable=False, default=False)
    emergency_contact: Mapped[bool] = mapped_column(nullable=False, default=False)
