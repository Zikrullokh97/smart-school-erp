from __future__ import annotations

from enum import StrEnum


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class SchoolStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class UserStatus(StrEnum):
    INVITED = "invited"
    ACTIVE = "active"
    DISABLED = "disabled"


class PersonStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"
    ARCHIVED = "archived"


class EnrollmentStatus(StrEnum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


class AttendanceSessionStatus(StrEnum):
    OPEN = "open"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    LOCKED = "locked"


class AttendanceEventType(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class AttendanceSource(StrEnum):
    MANUAL = "manual"
    FACE_ID = "face_id"
    IMPORT = "import"
    OFFLINE_SYNC = "offline_sync"


class BiometricStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class AIReportStatus(StrEnum):
    REQUESTED = "requested"
    PROCESSING = "processing"
    READY = "ready"
    REVIEWED = "reviewed"
    FAILED = "failed"


class SyncOperationStatus(StrEnum):
    RECEIVED = "received"
    APPLIED = "applied"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
