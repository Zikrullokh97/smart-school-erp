from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth.crud import get_tenant_by_slug, get_user_by_id, get_user_permissions
from smart_school.auth.security import ACCESS_TOKEN_TYPE, decode_jwt_token
from smart_school.db.session import get_session
from smart_school.models.enums import UserStatus
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_tenant(
    tenant_slug: Annotated[str, Header(..., alias="X-Tenant-Slug")],
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> Tenant:
    tenant = await get_tenant_by_slug(session, tenant_slug)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )
    return tenant


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)] = None,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> User:
    try:
        payload = decode_jwt_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    user_id = uuid.UUID(payload.get("sub", ""))
    token_tenant_id = uuid.UUID(payload.get("tenant_id", ""))
    if token_tenant_id != tenant.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tenant mismatch.",
        )

    user = await get_user_by_id(session, tenant.id, user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active.",
        )
    return user


def require_permission(permission_code: str):
    async def permission_dependency(
        user: Annotated[User, Depends(get_current_user)] = None,
        session: Annotated[AsyncSession, Depends(get_session)] = None,
    ) -> User:
        permissions = await get_user_permissions(session, user.tenant_id, user.id)
        if permission_code not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return user

    return permission_dependency
