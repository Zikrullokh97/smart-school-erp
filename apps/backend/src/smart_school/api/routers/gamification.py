from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.dependencies import (
    get_current_tenant,
    get_session,
    require_permission,
)
from smart_school.gamification import crud as gamification_crud
from smart_school.gamification import schemas as gamification_schemas
from smart_school.gamification import services as gamification_services
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/students", tags=["Gamification"])
students_read_permission = require_permission("students.read")
students_manage_permission = require_permission("students.manage")


@router.get(
    "/{student_id}/gamification", response_model=gamification_schemas.GamificationProfileRead
)
async def read_student_gamification(
    student_id: uuid.UUID,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> gamification_schemas.GamificationProfileRead:
    student = await gamification_crud.get_student_by_id(session, tenant.id, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    profile = await gamification_services.get_or_create_profile(session, tenant.id, student_id)
    gamification_profile = profile[0]
    badges = [
        {
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "xp_threshold": badge.xp_threshold,
            "metadata": badge.metadata_,
        }
        for _, badge in await gamification_services.get_student_badges(
            session, tenant.id, student_id
        )
    ]
    active_challenges = []
    return gamification_schemas.GamificationProfileRead(
        student_id=student_id,
        xp_total=gamification_profile.xp_total,
        level=gamification_profile.level,
        streak_count=gamification_profile.streak_count,
        streak_start_date=gamification_profile.streak_start_date,
        last_activity_at=gamification_profile.last_activity_at,
        badges=badges,
        active_challenges=active_challenges,
    )


@router.post(
    "/{student_id}/gamification/award", response_model=gamification_schemas.GamificationProfileRead
)
async def award_student_xp(
    student_id: uuid.UUID,
    payload: gamification_schemas.AwardXPRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> gamification_schemas.GamificationProfileRead:
    student = await gamification_crud.get_student_by_id(session, tenant.id, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    profile = await gamification_services.award_xp(
        session,
        tenant.id,
        student_id,
        payload.amount,
        payload.activity_type,
        payload.source,
        note=payload.note,
    )
    await session.commit()
    return gamification_schemas.GamificationProfileRead(
        student_id=student_id,
        xp_total=profile.xp_total,
        level=profile.level,
        streak_count=profile.streak_count,
        streak_start_date=profile.streak_start_date,
        last_activity_at=profile.last_activity_at,
        badges=[],
        active_challenges=[],
    )


@router.post(
    "/{student_id}/gamification/challenges/{challenge_code}/complete",
    response_model=gamification_schemas.StudentChallengeRead,
)
async def complete_challenge_for_student(
    student_id: uuid.UUID,
    challenge_code: str,
    payload: gamification_schemas.ChallengeCompleteRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_manage_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> gamification_schemas.StudentChallengeRead:
    student = await gamification_crud.get_student_by_id(session, tenant.id, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    try:
        student_challenge = await gamification_services.complete_challenge(
            session,
            tenant.id,
            student_id,
            challenge_code,
            evidence=payload.evidence,
            comment=payload.comment,
        )
        await session.commit()
        challenge = await gamification_crud.get_challenge_by_code(
            session, tenant.id, challenge_code
        )
        assert challenge is not None
        return gamification_schemas.StudentChallengeRead(
            challenge_id=challenge.id,
            code=challenge.code,
            name=challenge.name,
            description=challenge.description,
            xp_reward=challenge.xp_reward,
            goal_count=challenge.goal_count,
            status=student_challenge.status.value,
            progress_count=student_challenge.progress_count,
            completed_at=student_challenge.completed_at,
            metadata=student_challenge.metadata_,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/gamification/leaderboard", response_model=list[gamification_schemas.LeaderboardEntryRead]
)
async def list_gamification_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    _user: Annotated[User, Depends(students_read_permission)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[gamification_schemas.LeaderboardEntryRead]:
    leaderboard = await gamification_services.get_leaderboard(session, tenant.id, limit=limit)
    return [
        gamification_schemas.LeaderboardEntryRead(
            student_id=profile.student_id,
            student_number=student.student_number,
            first_name=student.first_name,
            last_name=student.last_name,
            xp_total=profile.xp_total,
            level=profile.level,
        )
        for profile, student in leaderboard
    ]
