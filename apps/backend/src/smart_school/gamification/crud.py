from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.gamification import (
    Badge,
    Challenge,
    GamificationProfile,
    StudentBadge,
    StudentChallenge,
)
from smart_school.models.people import Student


async def get_student_by_id(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> Student | None:
    result = await session.execute(select(Student).filter_by(tenant_id=tenant_id, id=student_id))
    return result.scalar_one_or_none()


async def get_profile(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> GamificationProfile | None:
    result = await session.execute(
        select(GamificationProfile).filter_by(tenant_id=tenant_id, student_id=student_id)
    )
    return result.scalar_one_or_none()


async def create_profile(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> GamificationProfile:
    profile = GamificationProfile(tenant_id=tenant_id, student_id=student_id)
    session.add(profile)
    await session.flush()
    return profile


async def list_leaderboard(session: AsyncSession, tenant_id: uuid.UUID, limit: int = 20) -> list[tuple[GamificationProfile, Student]]:
    result = await session.execute(
        select(GamificationProfile, Student)
        .join(Student, GamificationProfile.student_id == Student.id)
        .filter(GamificationProfile.tenant_id == tenant_id)
        .order_by(GamificationProfile.xp_total.desc(), GamificationProfile.level.desc())
        .limit(limit)
    )
    return result.all()


async def list_student_badges(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> list[tuple[StudentBadge, Badge]]:
    result = await session.execute(
        select(StudentBadge, Badge)
        .join(Badge, StudentBadge.badge_id == Badge.id)
        .filter(StudentBadge.tenant_id == tenant_id, StudentBadge.student_id == student_id)
    )
    return result.all()


async def get_challenge_by_code(session: AsyncSession, tenant_id: uuid.UUID, code: str) -> Challenge | None:
    result = await session.execute(select(Challenge).filter_by(tenant_id=tenant_id, code=code))
    return result.scalar_one_or_none()


async def get_student_challenge(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID, challenge_id: uuid.UUID) -> StudentChallenge | None:
    result = await session.execute(
        select(StudentChallenge).filter_by(
            tenant_id=tenant_id,
            student_id=student_id,
            challenge_id=challenge_id,
        )
    )
    return result.scalar_one_or_none()


async def list_student_challenges(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> list[tuple[StudentChallenge, Challenge]]:
    result = await session.execute(
        select(StudentChallenge, Challenge)
        .join(Challenge, StudentChallenge.challenge_id == Challenge.id)
        .filter(StudentChallenge.tenant_id == tenant_id, StudentChallenge.student_id == student_id)
    )
    return result.all()


async def create_student_challenge(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    challenge_id: uuid.UUID,
    progress_count: int = 0,
) -> StudentChallenge:
    student_challenge = StudentChallenge(
        tenant_id=tenant_id,
        student_id=student_id,
        challenge_id=challenge_id,
        progress_count=progress_count,
    )
    session.add(student_challenge)
    await session.flush()
    return student_challenge


async def assign_badge_to_student(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    badge_id: uuid.UUID,
    evidence: dict[str, Any] | None = None,
) -> StudentBadge:
    result = await session.execute(
        select(StudentBadge)
        .filter_by(tenant_id=tenant_id, student_id=student_id, badge_id=badge_id)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    student_badge = StudentBadge(
        tenant_id=tenant_id,
        student_id=student_id,
        badge_id=badge_id,
        evidence=evidence or {},
    )
    session.add(student_badge)
    await session.flush()
    return student_badge


async def list_badges_for_xp(session: AsyncSession, tenant_id: uuid.UUID, xp_total: int) -> list[Badge]:
    result = await session.execute(
        select(Badge)
        .filter(Badge.tenant_id == tenant_id, Badge.xp_threshold <= xp_total, Badge.active == True)
        .order_by(Badge.xp_threshold.asc())
    )
    return result.scalars().all()
