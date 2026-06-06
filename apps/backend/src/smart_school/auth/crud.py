from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.security import hash_password, hash_refresh_token
from smart_school.core.config import get_settings
from smart_school.models.auth import AuthSession
from smart_school.models.enums import UserStatus
from smart_school.models.identity import (
    Permission,
    Role,
    User,
    role_permissions_table,
    user_roles_table,
)
from smart_school.models.school import School
from smart_school.models.tenant import Tenant
from smart_school.seeds.initial_data import INITIAL_PERMISSIONS, INITIAL_ROLES


async def get_tenant_by_slug(session: AsyncSession, slug: str) -> Tenant | None:
    result = await session.execute(select(Tenant).filter_by(slug=slug))
    return result.scalar_one_or_none()


async def create_tenant(session: AsyncSession, slug: str, name: str) -> Tenant:
    tenant = Tenant(slug=slug, name=name)
    session.add(tenant)
    await session.flush()
    return tenant


async def create_school(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    name: str,
    code: str,
    region: str,
    district: str,
    address: str,
    timezone: str,
    language_code: str,
) -> School:
    school = School(
        tenant_id=tenant_id,
        name=name,
        code=code,
        region=region,
        district=district,
        address=address,
        timezone=timezone,
        language_code=language_code,
    )
    session.add(school)
    await session.flush()
    return school


async def ensure_permissions(session: AsyncSession) -> None:
    existing = {
        permission.code
        for permission in (await session.execute(select(Permission.code))).scalars().all()
    }
    for seed in INITIAL_PERMISSIONS:
        if seed.code not in existing:
            session.add(Permission(code=seed.code, description=seed.description))
    await session.flush()


async def ensure_tenant_roles(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    permissions = {
        permission.code: permission
        for permission in (await session.execute(select(Permission))).scalars().all()
    }
    existing_roles = {
        role.code
        for role in (await session.execute(select(Role).filter_by(tenant_id=tenant_id)))
        .scalars()
        .all()
    }
    for role_seed in INITIAL_ROLES:
        if role_seed.code in existing_roles:
            continue
        role = Role(
            tenant_id=tenant_id,
            code=role_seed.code,
            name=role_seed.name,
            description=role_seed.description,
            is_system=True,
        )
        session.add(role)
        await session.flush()
        for permission_code in role_seed.permissions:
            permission = permissions[permission_code]
            role.permissions.append(permission)
    await session.flush()


async def create_tenant_with_admin(
    session: AsyncSession,
    tenant_slug: str,
    tenant_name: str,
    school_name: str,
    school_code: str,
    region: str,
    district: str,
    address: str,
    timezone: str,
    language_code: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role_codes: list[str] | None = None,
) -> tuple[Tenant, School, User]:
    await ensure_permissions(session)
    tenant = await create_tenant(session, tenant_slug, tenant_name)
    await ensure_tenant_roles(session, tenant.id)
    school = await create_school(
        session,
        tenant.id,
        school_name,
        school_code,
        region,
        district,
        address,
        timezone,
        language_code,
    )
    user = await create_user(
        session,
        tenant.id,
        email,
        password,
        first_name,
        last_name,
        status=UserStatus.ACTIVE,
        locale="ky-KG",
        role_codes=role_codes or ["school_admin"],
    )
    return tenant, school, user


async def get_user_by_email(session: AsyncSession, tenant_id: uuid.UUID, email: str) -> User | None:
    result = await session.execute(select(User).filter_by(tenant_id=tenant_id, email=email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> User | None:
    result = await session.execute(select(User).filter_by(tenant_id=tenant_id, id=user_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    status: str = UserStatus.ACTIVE,
    locale: str = "ky-KG",
    external_ref: str | None = None,
    role_codes: list[str] | None = None,
) -> User:
    user = User(
        tenant_id=tenant_id,
        email=email.lower(),
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        locale=locale,
        status=status,
        external_ref=external_ref,
        profile={},
    )
    session.add(user)
    await session.flush()
    if role_codes:
        await assign_roles_to_user(session, tenant_id, user.id, role_codes)
    await session.flush()
    return user


async def assign_roles_to_user(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    role_codes: Iterable[str],
) -> None:
    roles = (
        (
            await session.execute(
                select(Role).filter_by(tenant_id=tenant_id).filter(Role.code.in_(role_codes))
            )
        )
        .scalars()
        .all()
    )
    if len(roles) != len(set(role_codes)):
        missing = set(role_codes) - {role.code for role in roles}
        raise ValueError(f"Missing role codes for tenant: {sorted(missing)}")
    rows = [
        {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role_id": role.id,
            "school_id": None,
        }
        for role in roles
    ]
    await session.execute(user_roles_table.insert(), rows)


async def create_auth_session(
    session: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    refresh_token: str,
    user_agent: str | None,
    ip_address: str | None,
) -> AuthSession:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_days)
    auth_session = AuthSession(
        tenant_id=tenant_id,
        user_id=user_id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at,
    )
    session.add(auth_session)
    await session.flush()
    return auth_session


async def get_auth_session_by_hash(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    refresh_token_hash: str,
) -> AuthSession | None:
    result = await session.execute(
        select(AuthSession).filter_by(tenant_id=tenant_id, refresh_token_hash=refresh_token_hash)
    )
    return result.scalar_one_or_none()


async def revoke_auth_session(session: AsyncSession, auth_session: AuthSession) -> None:
    auth_session.revoked_at = datetime.now(UTC)
    session.add(auth_session)
    await session.flush()


async def get_user_permissions(
    session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> set[str]:
    statement = (
        select(Permission.code)
        .select_from(user_roles_table)
        .join(Role, user_roles_table.c.role_id == Role.id)
        .join(role_permissions_table, role_permissions_table.c.role_id == Role.id)
        .join(Permission, Permission.id == role_permissions_table.c.permission_id)
        .where(
            user_roles_table.c.tenant_id == tenant_id,
            user_roles_table.c.user_id == user_id,
        )
    )
    rows = (await session.execute(statement)).scalars().all()
    return set(rows)
