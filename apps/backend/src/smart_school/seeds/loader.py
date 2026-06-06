from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.models.identity import Permission, Role
from smart_school.seeds.initial_data import INITIAL_PERMISSIONS, INITIAL_ROLES


async def ensure_permissions(session: AsyncSession) -> None:
    existing = {
        permission.code
        for permission in (await session.execute(select(Permission.code))).scalars().all()
    }
    for seed in INITIAL_PERMISSIONS:
        if seed.code not in existing:
            session.add(Permission(code=seed.code, description=seed.description))
    await session.flush()


async def ensure_tenant_roles(session: AsyncSession, tenant_id: str) -> None:
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
        for code in role_seed.permissions:
            permission = permissions[code]
            role.permissions.append(permission)
    await session.flush()
