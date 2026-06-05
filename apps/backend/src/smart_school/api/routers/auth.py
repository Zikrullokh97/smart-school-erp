from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from smart_school.auth import crud as auth_crud
from smart_school.auth.dependencies import (
    get_current_tenant,
    get_current_user,
    get_session,
)
from smart_school.auth.schemas import (
    AuthTokenRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TenantRegistrationRequest,
    TokenResponse,
    UserRead,
)
from smart_school.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from smart_school.models.identity import User
from smart_school.models.tenant import Tenant

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
async def login(
    request: Request,
    payload: AuthTokenRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TokenResponse:
    user = await auth_crud.get_user_by_email(session, tenant.id, payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active.",
        )

    access_token, expires_in = create_access_token(
        str(user.id),
        str(tenant.id),
    )
    refresh_token = create_refresh_token()
    user_agent = request.headers.get("user-agent")
    remote_addr = request.client.host if request.client else None
    await auth_crud.create_auth_session(
        session,
        user.id,
        tenant.id,
        refresh_token,
        user_agent,
        remote_addr,
    )
    await session.commit()
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TokenResponse:
    refresh_hash = hash_refresh_token(payload.refresh_token)
    session_record = await auth_crud.get_auth_session_by_hash(session, tenant.id, refresh_hash)
    if session_record is None or session_record.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    user = await auth_crud.get_user_by_id(session, tenant.id, session_record.user_id)
    if user is None or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    new_refresh_token = create_refresh_token()
    await auth_crud.revoke_auth_session(session, session_record)
    await auth_crud.create_auth_session(
        session,
        user.id,
        tenant.id,
        new_refresh_token,
        None,
        None,
    )
    access_token, expires_in = create_access_token(str(user.id), str(tenant.id))
    await session.commit()
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=new_refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> None:
    refresh_hash = hash_refresh_token(payload.refresh_token)
    session_record = await auth_crud.get_auth_session_by_hash(session, tenant.id, refresh_hash)
    if session_record is not None and session_record.user_id == current_user.id:
        await auth_crud.revoke_auth_session(session, session_record)
        await session.commit()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(
    payload: TenantRegistrationRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> TokenResponse:
    existing = await auth_crud.get_tenant_by_slug(session, payload.tenant_slug)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug is already taken.",
        )

    tenant, _school, user = await auth_crud.create_tenant_with_admin(
        session,
        payload.tenant_slug,
        payload.tenant_name,
        payload.school_name,
        payload.school_code,
        payload.region,
        payload.district,
        payload.address,
        "Asia/Bishkek",
        payload.email,
        payload.password,
        payload.first_name,
        payload.last_name,
    )
    access_token, expires_in = create_access_token(str(user.id), str(tenant.id))
    refresh_token = create_refresh_token()
    await auth_crud.create_auth_session(
        session,
        user.id,
        tenant.id,
        refresh_token,
        None,
        None,
    )
    await session.commit()
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> UserRead:
    role_codes = [role.code for role in current_user.roles]
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        status=current_user.status,
        locale=current_user.locale,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        role_codes=role_codes,
    )
