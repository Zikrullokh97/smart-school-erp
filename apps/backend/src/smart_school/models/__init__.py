from smart_school.db.base import Base
from smart_school.models.ai_reporting import AIReport
from smart_school.models.ai_review import AIReviewAction
from smart_school.models.auth import AuthSession
from smart_school.models.attendance import AttendanceEvent, AttendanceSession, FaceEmbedding
from smart_school.models.audit import AuditLog
from smart_school.models.identity import (
    Permission,
    Role,
    User,
    role_permissions_table,
    user_roles_table,
)
from smart_school.models.notifications import Notification
from smart_school.models.outbox import OutboxEvent
from smart_school.models.gamification import (
    Badge,
    Challenge,
    GamificationProfile,
    StudentBadge,
    StudentChallenge,
)
from smart_school.models.people import ParentProfile, ParentStudentLink, Student, Teacher
from smart_school.models.scheduling import Room, ScheduleConstraint, ScheduleSlot
from smart_school.models.school import AcademicYear, ClassEnrollment, ClassGroup, School, Term
from smart_school.models.sync import SyncDevice, SyncOperation
from smart_school.models.tenant import Tenant

__all__ = [
    "AIReport",
    "AIReviewAction",
    "AcademicYear",
    "AttendanceEvent",
    "AttendanceSession",
    "AuthSession",
    "AuditLog",
    "Badge",
    "Challenge",
    "FaceEmbedding",
    "GamificationProfile",
    "Notification",
    "OutboxEvent",
    "ParentProfile",
    "ParentStudentLink",
    "Permission",
    "Role",
    "Room",
    "ScheduleConstraint",
    "ScheduleSlot",
    "School",
    "Student",
    "StudentBadge",
    "StudentChallenge",
    "SyncDevice",
    "SyncOperation",
    "Teacher",
    "Tenant",
    "Term",
    "User",
    "role_permissions_table",
    "user_roles_table",
]
