from __future__ import annotations

from smart_school.seeds.initial_data import INITIAL_PERMISSIONS, INITIAL_ROLES, permission_codes


def test_permission_codes_are_unique() -> None:
    codes = [permission.code for permission in INITIAL_PERMISSIONS]
    assert len(codes) == len(set(codes))


def test_role_codes_are_unique() -> None:
    codes = [role.code for role in INITIAL_ROLES]
    assert len(codes) == len(set(codes))


def test_roles_reference_existing_permissions() -> None:
    permissions = permission_codes()
    for role in INITIAL_ROLES:
        assert role.permissions
        assert set(role.permissions).issubset(permissions)


def test_seed_data_covers_required_domains() -> None:
    required_prefixes = {
        "tenants",
        "schools",
        "users",
        "roles",
        "students",
        "teachers",
        "parents",
        "attendance",
        "face_id",
        "notifications",
        "ai_reports",
        "scheduling",
        "sync",
        "audit",
    }
    actual_prefixes = {
        permission.code.split(".", maxsplit=1)[0] for permission in INITIAL_PERMISSIONS
    }
    assert required_prefixes.issubset(actual_prefixes)
