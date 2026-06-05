from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.gamification import crud as gamification_crud
from smart_school.models.enums import ChallengeStatus
from smart_school.models.gamification import Badge, Challenge
from smart_school.gamification.crud import list_badges_for_xp


def _calculate_level(xp_total: int) -> int:
    return max(1, xp_total // 250 + 1)


def _should_increment_streak(last_activity_at: datetime | None, activity_time: datetime) -> bool:
    if last_activity_at is None:
        return True
    days_since = (activity_time.date() - last_activity_at.date()).days
    return days_since == 1


async def get_or_create_profile(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
) -> tuple[object, bool]:
    profile = await gamification_crud.get_profile(session, tenant_id, student_id)
    if profile is not None:
        return profile, False
    profile = await gamification_crud.create_profile(session, tenant_id, student_id)
    return profile, True


async def award_xp(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    amount: int,
    activity_type: str,
    source: str,
    note: str | None = None,
) -> object:
    profile = await gamification_crud.get_profile(session, tenant_id, student_id)
    if profile is None:
        profile = await gamification_crud.create_profile(session, tenant_id, student_id)

    now = datetime.now(timezone.utc)
    profile.xp_total += amount
    profile.level = _calculate_level(profile.xp_total)

    if _should_increment_streak(profile.last_activity_at, now):
        profile.streak_count += 1
        if profile.streak_start_date is None:
            profile.streak_start_date = now.date()
    else:
        profile.streak_count = 1
        profile.streak_start_date = now.date()

    profile.last_activity_at = now
    await session.flush()

    # Auto-assign badges whose xp_threshold is now satisfied
    try:
        badges = await gamification_crud.list_badges_for_xp(session, tenant_id, profile.xp_total)
    except AttributeError:
        badges = []

    for badge in badges:
        await gamification_crud.assign_badge_to_student(session, tenant_id, student_id, badge.id)
    return profile


async def complete_challenge(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    student_id: uuid.UUID,
    challenge_code: str,
    evidence: dict[str, object] | None = None,
    comment: str | None = None,
) -> object:
    challenge = await gamification_crud.get_challenge_by_code(session, tenant_id, challenge_code)
    if challenge is None:
        raise ValueError("Challenge not found.")
    if not challenge.active:
        raise ValueError("Challenge is not active.")

    student_challenge = await gamification_crud.get_student_challenge(session, tenant_id, student_id, challenge.id)
    if student_challenge is None:
        student_challenge = await gamification_crud.create_student_challenge(
            session,
            tenant_id,
            student_id,
            challenge.id,
            progress_count=challenge.goal_count,
        )
    if student_challenge.status == ChallengeStatus.COMPLETED:
        return student_challenge

    student_challenge.progress_count = challenge.goal_count
    student_challenge.status = ChallengeStatus.COMPLETED
    student_challenge.completed_at = datetime.now(timezone.utc)
    student_challenge.metadata_["comment"] = comment or ""
    student_challenge.metadata_["evidence"] = evidence or {}
    await session.flush()

    await award_xp(
        session,
        tenant_id,
        student_id,
        challenge.xp_reward,
        activity_type="challenge_completion",
        source=challenge.code,
        note=comment,
    )

    return student_challenge


async def get_leaderboard(session: AsyncSession, tenant_id: uuid.UUID, limit: int = 20) -> list[tuple[object, object]]:
    return await gamification_crud.list_leaderboard(session, tenant_id, limit=limit)


async def get_student_badges(session: AsyncSession, tenant_id: uuid.UUID, student_id: uuid.UUID) -> list[tuple[object, Badge]]:
    return await gamification_crud.list_student_badges(session, tenant_id, student_id)
