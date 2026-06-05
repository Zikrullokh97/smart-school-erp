"""initial database schema

Revision ID: 20260604_0001
Revises:
Create Date: 2026-06-04 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "20260604_0001"
down_revision = None
branch_labels = None
depends_on = None


tenant_status = postgresql.ENUM("active", "suspended", "archived", name="tenant_status")
school_status = postgresql.ENUM("active", "inactive", "archived", name="school_status")
user_status = postgresql.ENUM("invited", "active", "disabled", name="user_status")
person_status = postgresql.ENUM(
    "active", "inactive", "graduated", "transferred", "archived", name="person_status"
)
teacher_status = postgresql.ENUM(
    "active", "inactive", "graduated", "transferred", "archived", name="teacher_status"
)
enrollment_status = postgresql.ENUM(
    "active", "withdrawn", "completed", name="enrollment_status"
)
attendance_session_status = postgresql.ENUM(
    "open", "submitted", "approved", "locked", name="attendance_session_status"
)
attendance_event_type = postgresql.ENUM(
    "present",
    "absent",
    "late",
    "excused",
    "check_in",
    "check_out",
    name="attendance_event_type",
)
attendance_source = postgresql.ENUM(
    "manual", "face_id", "import", "offline_sync", name="attendance_source"
)
biometric_status = postgresql.ENUM("active", "revoked", "expired", name="biometric_status")
notification_channel = postgresql.ENUM(
    "in_app", "email", "sms", "push", name="notification_channel"
)
notification_status = postgresql.ENUM(
    "pending", "sent", "read", "failed", name="notification_status"
)
ai_report_status = postgresql.ENUM(
    "requested", "processing", "ready", "reviewed", "failed", name="ai_report_status"
)
sync_operation_status = postgresql.ENUM(
    "received", "applied", "conflicted", "rejected", name="sync_operation_status"
)
outbox_status = postgresql.ENUM(
    "pending", "processing", "published", "failed", name="outbox_status"
)

enum_types = (
    tenant_status,
    school_status,
    user_status,
    person_status,
    teacher_status,
    enrollment_status,
    attendance_session_status,
    attendance_event_type,
    attendance_source,
    biometric_status,
    notification_channel,
    notification_status,
    ai_report_status,
    sync_operation_status,
    outbox_status,
)


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False)


def tenant_fk() -> sa.Column:
    return sa.Column(
        "tenant_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )


def timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def jsonb_column(name: str) -> sa.Column:
    return sa.Column(
        name,
        postgresql.JSONB(astext_type=sa.Text()),
        server_default=sa.text("'{}'::jsonb"),
        nullable=False,
    )


def create_tenant_index(table_name: str) -> None:
    op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    for enum_type in enum_types:
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "tenants",
        uuid_pk(),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", tenant_status, server_default="active", nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_tenants"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    op.create_table(
        "permissions",
        uuid_pk(),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)

    op.create_table(
        "schools",
        uuid_pk(),
        tenant_fk(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=False),
        sa.Column("district", sa.String(length=120), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("language_code", sa.String(length=16), nullable=False),
        sa.Column("status", school_status, server_default="active", nullable=False),
        jsonb_column("settings"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_schools"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_schools_tenant_code"),
    )
    create_tenant_index("schools")

    op.create_table(
        "users",
        uuid_pk(),
        tenant_fk(),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("status", user_status, server_default="invited", nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("external_ref", sa.String(length=120), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        jsonb_column("profile"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        sa.UniqueConstraint("tenant_id", "external_ref", name="uq_users_tenant_external_ref"),
    )
    create_tenant_index("users")

    op.create_table(
        "roles",
        uuid_pk(),
        tenant_fk(),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_roles_tenant_code"),
    )
    create_tenant_index("roles")

    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_permission"),
    )

    op.create_table(
        "user_roles",
        tenant_fk(),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "user_id",
            "role_id",
            "school_id",
            name="uq_user_roles_scope",
        ),
    )
    create_tenant_index("user_roles")

    op.create_table(
        "academic_years",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_academic_years"),
        sa.UniqueConstraint("tenant_id", "school_id", "name", name="uq_academic_years_school_name"),
    )
    create_tenant_index("academic_years")
    op.create_index("ix_academic_years_school_id", "academic_years", ["school_id"])

    op.create_table(
        "terms",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "academic_year_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_terms"),
        sa.UniqueConstraint("tenant_id", "academic_year_id", "name", name="uq_terms_year_name"),
    )
    create_tenant_index("terms")
    op.create_index("ix_terms_school_id", "terms", ["school_id"])
    op.create_index("ix_terms_academic_year_id", "terms", ["academic_year_id"])

    op.create_table(
        "students",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("student_number", sa.String(length=80), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("middle_name", sa.String(length=120), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=32), nullable=False),
        sa.Column("status", person_status, server_default="active", nullable=False),
        sa.Column("enrollment_date", sa.Date(), nullable=False),
        jsonb_column("profile"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_students"),
        sa.UniqueConstraint("tenant_id", "school_id", "student_number", name="uq_students_number"),
    )
    create_tenant_index("students")
    op.create_index("ix_students_school_id", "students", ["school_id"])

    op.create_table(
        "teachers",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("employee_number", sa.String(length=80), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("status", teacher_status, server_default="active", nullable=False),
        jsonb_column("profile"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_teachers"),
        sa.UniqueConstraint("tenant_id", "school_id", "employee_number", name="uq_teachers_number"),
    )
    create_tenant_index("teachers")
    op.create_index("ix_teachers_school_id", "teachers", ["school_id"])
    op.create_index("ix_teachers_user_id", "teachers", ["user_id"])

    op.create_table(
        "parent_profiles",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("phone_number", sa.String(length=40), nullable=False),
        sa.Column("preferred_language", sa.String(length=16), nullable=False),
        jsonb_column("profile"),
        jsonb_column("ui_preferences"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_parent_profiles"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_parent_profiles_user"),
    )
    create_tenant_index("parent_profiles")
    op.create_index("ix_parent_profiles_user_id", "parent_profiles", ["user_id"])

    op.create_table(
        "parent_student_links",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "parent_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("parent_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relationship", sa.String(length=80), nullable=False),
        sa.Column("can_pick_up", sa.Boolean(), nullable=False),
        sa.Column("emergency_contact", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_parent_student_links"),
        sa.UniqueConstraint(
            "tenant_id",
            "parent_profile_id",
            "student_id",
            name="uq_parent_student",
        ),
    )
    create_tenant_index("parent_student_links")
    op.create_index(
        "ix_parent_student_links_parent_profile_id",
        "parent_student_links",
        ["parent_profile_id"],
    )
    op.create_index("ix_parent_student_links_student_id", "parent_student_links", ["student_id"])

    op.create_table(
        "class_groups",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "academic_year_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "homeroom_teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teachers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_class_groups"),
        sa.UniqueConstraint(
            "tenant_id",
            "school_id",
            "academic_year_id",
            "grade_level",
            "section",
            name="uq_class_groups_school_year_grade_section",
        ),
    )
    create_tenant_index("class_groups")
    op.create_index("ix_class_groups_school_id", "class_groups", ["school_id"])
    op.create_index("ix_class_groups_academic_year_id", "class_groups", ["academic_year_id"])
    op.create_index("ix_class_groups_homeroom_teacher_id", "class_groups", ["homeroom_teacher_id"])

    op.create_table(
        "class_enrollments",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "class_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("class_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", enrollment_status, server_default="active", nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_class_enrollments"),
        sa.UniqueConstraint(
            "tenant_id",
            "class_group_id",
            "student_id",
            name="uq_class_enrollments",
        ),
    )
    create_tenant_index("class_enrollments")
    op.create_index("ix_class_enrollments_class_group_id", "class_enrollments", ["class_group_id"])
    op.create_index("ix_class_enrollments_student_id", "class_enrollments", ["student_id"])

    op.create_table(
        "rooms",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        jsonb_column("attributes"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_rooms"),
        sa.UniqueConstraint("tenant_id", "school_id", "code", name="uq_rooms_code"),
    )
    create_tenant_index("rooms")
    op.create_index("ix_rooms_school_id", "rooms", ["school_id"])

    op.create_table(
        "schedule_constraints",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("constraint_type", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        jsonb_column("rule"),
        sa.Column("priority", sa.Integer(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_schedule_constraints"),
    )
    create_tenant_index("schedule_constraints")
    op.create_index("ix_schedule_constraints_school_id", "schedule_constraints", ["school_id"])
    op.create_index(
        "ix_schedule_constraints_constraint_type",
        "schedule_constraints",
        ["constraint_type"],
    )

    op.create_table(
        "schedule_slots",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "class_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("class_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teachers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "room_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rooms.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("period_code", sa.String(length=40), nullable=False),
        sa.Column("starts_at", sa.Time(timezone=True), nullable=False),
        sa.Column("ends_at", sa.Time(timezone=True), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_schedule_slots"),
        sa.UniqueConstraint(
            "tenant_id",
            "class_group_id",
            "weekday",
            "period_code",
            name="uq_schedule_slots_class_period",
        ),
    )
    create_tenant_index("schedule_slots")
    op.create_index("ix_schedule_slots_school_id", "schedule_slots", ["school_id"])
    op.create_index("ix_schedule_slots_class_group_id", "schedule_slots", ["class_group_id"])
    op.create_index("ix_schedule_slots_teacher_id", "schedule_slots", ["teacher_id"])
    op.create_index("ix_schedule_slots_room_id", "schedule_slots", ["room_id"])

    op.create_table(
        "attendance_sessions",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "class_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("class_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teachers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("period_code", sa.String(length=40), nullable=False),
        sa.Column("starts_at", sa.Time(timezone=True), nullable=True),
        sa.Column("ends_at", sa.Time(timezone=True), nullable=True),
        sa.Column("status", attendance_session_status, server_default="open", nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_attendance_sessions"),
        sa.UniqueConstraint(
            "tenant_id",
            "class_group_id",
            "session_date",
            "period_code",
            name="uq_attendance_sessions_period",
        ),
    )
    create_tenant_index("attendance_sessions")
    op.create_index("ix_attendance_sessions_school_id", "attendance_sessions", ["school_id"])
    op.create_index(
        "ix_attendance_sessions_class_group_id",
        "attendance_sessions",
        ["class_group_id"],
    )
    op.create_index("ix_attendance_sessions_teacher_id", "attendance_sessions", ["teacher_id"])
    op.create_index("ix_attendance_sessions_session_date", "attendance_sessions", ["session_date"])

    op.create_table(
        "attendance_events",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", attendance_event_type, nullable=False),
        sa.Column("source", attendance_source, nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "captured_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        jsonb_column("evidence"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_attendance_events"),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_attendance_events_idempotency",
        ),
    )
    create_tenant_index("attendance_events")
    op.create_index("ix_attendance_events_session_id", "attendance_events", ["session_id"])
    op.create_index("ix_attendance_events_student_id", "attendance_events", ["student_id"])
    op.create_index("ix_attendance_events_captured_at", "attendance_events", ["captured_at"])
    op.create_index(
        "ix_attendance_events_captured_by_user_id",
        "attendance_events",
        ["captured_by_user_id"],
    )

    op.create_table(
        "face_embeddings",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("embedding", Vector(512), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("consent_reference", sa.String(length=160), nullable=False),
        sa.Column("consent_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", biometric_status, server_default="active", nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_face_embeddings"),
        sa.UniqueConstraint(
            "tenant_id",
            "student_id",
            "model_name",
            "model_version",
            name="uq_face_embeddings_student_model",
        ),
    )
    create_tenant_index("face_embeddings")
    op.create_index("ix_face_embeddings_student_id", "face_embeddings", ["student_id"])

    op.create_table(
        "notifications",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "recipient_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("status", notification_status, server_default="pending", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=4000), nullable=False),
        sa.Column("template_code", sa.String(length=120), nullable=True),
        jsonb_column("payload"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(length=1000), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )
    create_tenant_index("notifications")
    op.create_index("ix_notifications_recipient_user_id", "notifications", ["recipient_user_id"])

    op.create_table(
        "ai_reports",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "requested_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("report_type", sa.String(length=120), nullable=False),
        sa.Column("status", ai_report_status, server_default="requested", nullable=False),
        sa.Column("prompt_hash", sa.String(length=128), nullable=False),
        jsonb_column("input_parameters"),
        jsonb_column("source_references"),
        sa.Column("output_summary", sa.String(length=8000), nullable=True),
        sa.Column("output_embedding", Vector(1536), nullable=True),
        sa.Column(
            "reviewed_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_ai_reports"),
    )
    create_tenant_index("ai_reports")
    op.create_index("ix_ai_reports_requested_by_user_id", "ai_reports", ["requested_by_user_id"])
    op.create_index("ix_ai_reports_school_id", "ai_reports", ["school_id"])
    op.create_index("ix_ai_reports_report_type", "ai_reports", ["report_type"])
    op.create_index("ix_ai_reports_reviewed_by_user_id", "ai_reports", ["reviewed_by_user_id"])

    op.create_table(
        "ai_review_actions",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "ai_report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("decision", sa.String(length=80), nullable=False),
        sa.Column("comment", sa.String(length=2000), nullable=True),
        jsonb_column("explainability"),
        jsonb_column("metadata"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_ai_review_actions"),
        sa.UniqueConstraint("tenant_id", "ai_report_id", "actor_user_id", "created_at", name="uq_ai_review_actions"),
    )
    create_tenant_index("ai_review_actions")
    op.create_index("ix_ai_review_actions_ai_report_id", "ai_review_actions", ["ai_report_id"])

    op.create_table(
        "sync_devices",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("device_key", sa.String(length=160), nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("app_version", sa.String(length=40), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_sync_devices"),
        sa.UniqueConstraint("tenant_id", "device_key", name="uq_sync_devices_key"),
    )
    create_tenant_index("sync_devices")
    op.create_index("ix_sync_devices_user_id", "sync_devices", ["user_id"])

    op.create_table(
        "gamification_profiles",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("xp_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("streak_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak_start_date", sa.Date(), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_gamification_profiles"),
        sa.UniqueConstraint("tenant_id", "student_id", name="uq_gamification_profiles_student"),
    )
    create_tenant_index("gamification_profiles")
    op.create_index("ix_gamification_profiles_student_id", "gamification_profiles", ["student_id"])

    op.create_table(
        "badges",
        uuid_pk(),
        tenant_fk(),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("icon", sa.String(length=120), nullable=True),
        sa.Column("xp_threshold", sa.Integer(), nullable=False, server_default="0"),
        jsonb_column("metadata"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_badges"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_badges_code"),
    )
    create_tenant_index("badges")

    op.create_table(
        "student_badges",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "badge_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("badges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        jsonb_column("evidence"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_student_badges"),
        sa.UniqueConstraint("tenant_id", "student_id", "badge_id", name="uq_student_badges"),
    )
    create_tenant_index("student_badges")
    op.create_index("ix_student_badges_student_id", "student_badges", ["student_id"])
    op.create_index("ix_student_badges_badge_id", "student_badges", ["badge_id"])

    op.create_table(
        "challenges",
        uuid_pk(),
        tenant_fk(),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goal_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        jsonb_column("metadata"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_challenges"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_challenges_code"),
    )
    create_tenant_index("challenges")

    op.create_table(
        "student_challenges",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "challenge_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("challenges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", challenge_status, nullable=False, server_default="pending"),
        sa.Column("progress_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        jsonb_column("metadata"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_student_challenges"),
        sa.UniqueConstraint("tenant_id", "student_id", "challenge_id", name="uq_student_challenges"),
    )
    create_tenant_index("student_challenges")
    op.create_index("ix_student_challenges_student_id", "student_challenges", ["student_id"])
    op.create_index("ix_student_challenges_challenge_id", "student_challenges", ["challenge_id"])

    op.create_table(
        "sync_operations",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sync_devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("operation_id", sa.String(length=160), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operation_type", sa.String(length=80), nullable=False),
        sa.Column("payload_version", sa.Integer(), nullable=False),
        jsonb_column("payload"),
        sa.Column("base_revision", sa.String(length=120), nullable=True),
        sa.Column("status", sync_operation_status, server_default="received", nullable=False),
        jsonb_column("conflict_details"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_sync_operations"),
        sa.UniqueConstraint("tenant_id", "device_id", "operation_id", name="uq_sync_operations"),
    )
    create_tenant_index("sync_operations")
    op.create_index("ix_sync_operations_device_id", "sync_operations", ["device_id"])
    op.create_index("ix_sync_operations_user_id", "sync_operations", ["user_id"])

    op.create_table(
        "audit_logs",
        uuid_pk(),
        tenant_fk(),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        jsonb_column("summary"),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    create_tenant_index("audit_logs")
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])

    op.create_table(
        "outbox_events",
        uuid_pk(),
        tenant_fk(),
        sa.Column("aggregate_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_id", sa.String(length=120), nullable=False),
        sa.Column("event_type", sa.String(length=160), nullable=False),
        jsonb_column("payload"),
        sa.Column("status", outbox_status, server_default="pending", nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.String(length=2000), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_outbox_events"),
    )
    create_tenant_index("outbox_events")
    op.create_index("ix_outbox_events_aggregate_type", "outbox_events", ["aggregate_type"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])


def downgrade() -> None:
    for table_name in (
        "outbox_events",
        "audit_logs",
        "sync_operations",
        "sync_devices",
        "ai_reports",
        "notifications",
        "face_embeddings",
        "attendance_events",
        "attendance_sessions",
        "schedule_slots",
        "schedule_constraints",
        "rooms",
        "class_enrollments",
        "class_groups",
        "parent_student_links",
        "parent_profiles",
        "teachers",
        "students",
        "terms",
        "academic_years",
        "user_roles",
        "role_permissions",
        "roles",
        "users",
        "schools",
        "permissions",
        "tenants",
    ):
        op.drop_table(table_name)

    bind = op.get_bind()
    for enum_type in reversed(enum_types):
        enum_type.drop(bind, checkfirst=True)
