from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.people import ParentProfile, ParentStudentLink, Student


async def get_parent_profile_by_id(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
) -> ParentProfile | None:
    result = await session.execute(
        select(ParentProfile).filter_by(tenant_id=tenant_id, id=parent_profile_id)
    )
    return result.scalar_one_or_none()


async def list_parent_profiles(session: AsyncSession, tenant_id: uuid.UUID) -> list[ParentProfile]:
    result = await session.execute(select(ParentProfile).filter_by(tenant_id=tenant_id))
    return result.scalars().all()


async def create_parent_profile(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    phone_number: str,
    preferred_language: str,
    profile: dict[str, object] | None = None,
    ui_preferences: dict[str, object] | None = None,
) -> ParentProfile:
    parent_profile = ParentProfile(
        tenant_id=tenant_id,
        user_id=user_id,
        phone_number=phone_number,
        preferred_language=preferred_language,
        profile=profile or {},
        ui_preferences=ui_preferences or {},
    )
    session.add(parent_profile)
    await session.flush()
    return parent_profile


async def update_parent_profile(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    phone_number: str | None = None,
    preferred_language: str | None = None,
    profile: dict[str, object] | None = None,
    ui_preferences: dict[str, object] | None = None,
) -> ParentProfile | None:
    parent_profile = await get_parent_profile_by_id(session, tenant_id, parent_profile_id)
    if parent_profile is None:
        return None

    if user_id is not None:
        parent_profile.user_id = user_id
    if phone_number is not None:
        parent_profile.phone_number = phone_number
    if preferred_language is not None:
        parent_profile.preferred_language = preferred_language
    if profile is not None:
        parent_profile.profile = profile
    if ui_preferences is not None:
        parent_profile.ui_preferences = ui_preferences

    await session.flush()
    return parent_profile


async def list_parent_student_links(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
) -> list[ParentStudentLink]:
    result = await session.execute(
        select(ParentStudentLink).filter_by(
            tenant_id=tenant_id, parent_profile_id=parent_profile_id
        )
    )
    return result.scalars().all()


async def get_parent_student_link(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
    student_id: uuid.UUID,
) -> ParentStudentLink | None:
    result = await session.execute(
        select(ParentStudentLink).filter_by(
            tenant_id=tenant_id,
            parent_profile_id=parent_profile_id,
            student_id=student_id,
        )
    )
    return result.scalar_one_or_none()


async def create_parent_student_link(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
    student_id: uuid.UUID,
    relationship: str,
    can_pick_up: bool,
    emergency_contact: bool,
) -> ParentStudentLink:
    parent_profile = await get_parent_profile_by_id(session, tenant_id, parent_profile_id)
    if parent_profile is None:
        raise ValueError("Parent profile not found.")

    student = await session.execute(select(Student).filter_by(tenant_id=tenant_id, id=student_id))
    if student.scalar_one_or_none() is None:
        raise ValueError("Student not found.")

    link = ParentStudentLink(
        tenant_id=tenant_id,
        parent_profile_id=parent_profile_id,
        student_id=student_id,
        relationship=relationship,
        can_pick_up=can_pick_up,
        emergency_contact=emergency_contact,
    )
    session.add(link)
    await session.flush()
    return link


async def delete_parent_student_link(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    parent_profile_id: uuid.UUID,
    student_id: uuid.UUID,
) -> bool:
    link = await get_parent_student_link(session, tenant_id, parent_profile_id, student_id)
    if link is None:
        return False
    await session.delete(link)
    await session.flush()
    return True
