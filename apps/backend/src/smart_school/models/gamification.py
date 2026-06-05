from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_school.db.base import Base
from smart_school.models.common import enum_type
from smart_school.models.enums import ChallengeStatus
from smart_school.models.mixins import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class GamificationProfile(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "gamification_profiles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "student_id", name="uq_gamification_profiles_student"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    streak_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Badge(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "badges"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_badges_code"),
    )

    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(120), nullable=True)
    xp_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    metadata_: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class StudentBadge(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "student_badges"
    __table_args__ = (
        UniqueConstraint("tenant_id", "student_id", "badge_id", name="uq_student_badges"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    badge_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("badges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class Challenge(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "challenges"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_challenges_code"),
    )

    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    goal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="true")
    metadata_: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class StudentChallenge(UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "student_challenges"
    __table_args__ = (
        UniqueConstraint("tenant_id", "student_id", "challenge_id", name="uq_student_challenges"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ChallengeStatus] = mapped_column(
        enum_type(ChallengeStatus, "challenge_status"),
        nullable=False,
        default=ChallengeStatus.PENDING,
        server_default=ChallengeStatus.PENDING.value,
    )
    progress_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
