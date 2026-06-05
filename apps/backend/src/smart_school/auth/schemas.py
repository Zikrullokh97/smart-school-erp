from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
    expires_in: int
    refresh_token: str


class AuthTokenRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TenantRegistrationRequest(BaseModel):
    tenant_slug: constr(min_length=3, max_length=80, pattern=r"^[a-z0-9-]+$")
    tenant_name: constr(min_length=3, max_length=255)
    school_name: constr(min_length=3, max_length=255)
    school_code: constr(min_length=1, max_length=80)
    region: constr(min_length=1, max_length=120)
    district: constr(min_length=1, max_length=120)
    address: constr(min_length=1, max_length=500)
    email: EmailStr
    password: constr(min_length=8)
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)


class TenantRead(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    locale: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    locale: constr(min_length=2, max_length=16) = Field(default="ky-KG")
    status: str = Field(default="active")
    role_codes: list[str] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    first_name: constr(min_length=1, max_length=120) | None = None
    last_name: constr(min_length=1, max_length=120) | None = None
    locale: constr(min_length=2, max_length=16) | None = None
    status: str | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    status: str
    locale: str
    created_at: datetime
    updated_at: datetime
    role_codes: list[str]

    model_config = ConfigDict(from_attributes=True)


class SchoolCreateRequest(BaseModel):
    name: constr(min_length=3, max_length=255)
    code: constr(min_length=1, max_length=80)
    region: constr(min_length=1, max_length=120)
    district: constr(min_length=1, max_length=120)
    address: constr(min_length=1, max_length=500)
    timezone: constr(min_length=1, max_length=64) = Field(default="Asia/Bishkek")
    language_code: constr(min_length=2, max_length=16) = Field(default="ky-KG")


class SchoolRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    region: str
    district: str
    address: str
    timezone: str
    language_code: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
