from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from smart_school.models import Base

EXPECTED_TABLES = {
    "academic_years",
    "ai_reports",
    "attendance_events",
    "attendance_sessions",
    "auth_sessions",
    "audit_logs",
    "class_enrollments",
    "class_groups",
    "face_embeddings",
    "notifications",
    "outbox_events",
    "parent_profiles",
    "parent_student_links",
    "ai_review_actions",
    "badges",
    "challenges",
    "gamification_profiles",
    "student_badges",
    "student_challenges",
    "permissions",
    "role_permissions",
    "roles",
    "rooms",
    "schedule_constraints",
    "schedule_slots",
    "schools",
    "students",
    "sync_devices",
    "sync_operations",
    "teachers",
    "tenants",
    "terms",
    "user_roles",
    "users",
}

TENANT_SCOPED_TABLES = EXPECTED_TABLES - {"permissions", "role_permissions", "tenants"}


def test_metadata_contains_expected_core_tables() -> None:
    assert EXPECTED_TABLES.issubset(Base.metadata.tables.keys())


def test_tenant_scoped_tables_have_required_tenant_column() -> None:
    for table_name in TENANT_SCOPED_TABLES:
        table = Base.metadata.tables[table_name]
        assert "tenant_id" in table.c, f"{table_name} must carry tenant_id"
        assert not table.c.tenant_id.nullable, f"{table_name}.tenant_id must be required"


def test_tenant_scoped_tables_have_tenant_index_or_unique_scope() -> None:
    for table_name in TENANT_SCOPED_TABLES:
        table = Base.metadata.tables[table_name]
        has_tenant_index = any(
            "tenant_id" in [column.name for column in index.columns] for index in table.indexes
        )
        has_tenant_unique = any(
            isinstance(constraint, UniqueConstraint)
            and "tenant_id" in [column.name for column in constraint.columns]
            for constraint in table.constraints
        )
        assert has_tenant_index or has_tenant_unique, f"{table_name} needs tenant query support"


def test_core_uniqueness_rules_include_tenant_scope() -> None:
    uniqueness_expectations = {
        "schools": ("tenant_id", "code"),
        "users": ("tenant_id", "email"),
        "roles": ("tenant_id", "code"),
        "students": ("tenant_id", "school_id", "student_number"),
        "teachers": ("tenant_id", "school_id", "employee_number"),
        "sync_operations": ("tenant_id", "device_id", "operation_id"),
    }

    for table_name, expected_columns in uniqueness_expectations.items():
        table = Base.metadata.tables[table_name]
        unique_sets = {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        assert expected_columns in unique_sets


def test_metadata_compiles_for_postgresql() -> None:
    dialect = postgresql.dialect()
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert f"CREATE TABLE {table.name}" in ddl
