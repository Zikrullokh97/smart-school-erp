from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionSeed:
    code: str
    description: str


@dataclass(frozen=True)
class RoleSeed:
    code: str
    name: str
    description: str
    permissions: tuple[str, ...]


INITIAL_PERMISSIONS: tuple[PermissionSeed, ...] = (
    PermissionSeed("tenants.manage", "Manage tenant lifecycle and platform configuration."),
    PermissionSeed("schools.read", "Read school records and school-level settings."),
    PermissionSeed("schools.manage", "Manage school records and school-level settings."),
    PermissionSeed("users.read", "Read users and account status."),
    PermissionSeed("users.manage", "Manage users, invitations, and account status."),
    PermissionSeed("roles.manage", "Manage roles and permission assignments."),
    PermissionSeed("students.read", "Read student records."),
    PermissionSeed("students.manage", "Create and update student records."),
    PermissionSeed("teachers.read", "Read teacher records."),
    PermissionSeed("teachers.manage", "Create and update teacher records."),
    PermissionSeed("parents.read", "Read parent and guardian records."),
    PermissionSeed("parents.manage", "Create and update parent and guardian records."),
    PermissionSeed("attendance.read", "Read attendance sessions, events, and summaries."),
    PermissionSeed("attendance.capture", "Capture attendance events."),
    PermissionSeed("attendance.manage", "Approve, correct, and lock attendance records."),
    PermissionSeed("face_id.manage", "Manage consent-aware face identity records."),
    PermissionSeed("notifications.read", "Read notification inbox records."),
    PermissionSeed("notifications.manage", "Create and manage notifications."),
    PermissionSeed("ai_reports.read", "Read generated AI report records."),
    PermissionSeed("ai_reports.manage", "Request, review, and manage AI reports."),
    PermissionSeed("scheduling.read", "Read schedule records and proposals."),
    PermissionSeed("scheduling.manage", "Create and manage schedules and constraints."),
    PermissionSeed("sync.manage", "Manage offline sync devices and conflict records."),
    PermissionSeed("audit.read", "Read audit logs."),
)

INITIAL_ROLES: tuple[RoleSeed, ...] = (
    RoleSeed(
        "platform_owner",
        "Platform Owner",
        "Full platform administration role.",
        tuple(permission.code for permission in INITIAL_PERMISSIONS),
    ),
    RoleSeed(
        "school_admin",
        "School Administrator",
        "School-level administrator for operations and reporting.",
        (
            "schools.read",
            "schools.manage",
            "users.read",
            "users.manage",
            "roles.manage",
            "students.read",
            "students.manage",
            "teachers.read",
            "teachers.manage",
            "parents.read",
            "parents.manage",
            "attendance.read",
            "attendance.manage",
            "face_id.manage",
            "notifications.read",
            "notifications.manage",
            "ai_reports.read",
            "ai_reports.manage",
            "scheduling.read",
            "scheduling.manage",
            "sync.manage",
            "audit.read",
        ),
    ),
    RoleSeed(
        "teacher",
        "Teacher",
        "Teacher role for class operations and attendance capture.",
        (
            "schools.read",
            "students.read",
            "parents.read",
            "attendance.read",
            "attendance.capture",
            "notifications.read",
            "scheduling.read",
        ),
    ),
    RoleSeed(
        "parent",
        "Parent",
        "Parent and guardian role for student visibility and communication.",
        (
            "schools.read",
            "students.read",
            "attendance.read",
            "notifications.read",
        ),
    ),
    RoleSeed(
        "attendance_operator",
        "Attendance Operator",
        "Operational role for attendance collection and sync review.",
        (
            "schools.read",
            "students.read",
            "attendance.read",
            "attendance.capture",
            "sync.manage",
        ),
    ),
)


def permission_codes() -> set[str]:
    return {permission.code for permission in INITIAL_PERMISSIONS}


def role_codes() -> set[str]:
    return {role.code for role in INITIAL_ROLES}
