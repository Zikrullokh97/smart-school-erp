# Authentication API

## Overview

The backend authentication module supports tenant-scoped user management, JWT access tokens, refresh token sessions, and RBAC permission enforcement.

## Endpoints

### `POST /api/v1/auth/register`

Registers a new tenant and initial school with an administrator user.

Request body:
- `tenant_slug`: Tenant identifier for tenant scoping.
- `tenant_name`: Full tenant name.
- `school_name`: Primary school name.
- `school_code`: Unique code for the initial school.
- `region`: Administrative region.
- `district`: School district.
- `address`: School address.
- `email`: Administrator login email.
- `password`: Administrator password.
- `first_name`: User first name.
- `last_name`: User last name.

Response:
- `access_token`
- `token_type`
- `expires_in`
- `refresh_token`

### `POST /api/v1/auth/token`

Authenticates an existing user and returns a JWT access token plus refresh token.

Headers:
- `X-Tenant-Slug`: Tenant slug identifying the tenant context.

Request body:
- `email`
- `password`

### `POST /api/v1/auth/refresh`

Rotates refresh tokens and issues a new access token.

Headers:
- `X-Tenant-Slug`

Request body:
- `refresh_token`

### `POST /api/v1/auth/logout`

Revokes the current refresh token session.

Headers:
- `X-Tenant-Slug`
- `Authorization: Bearer <access_token>`

Request body:
- `refresh_token`

### `GET /api/v1/auth/me`

Returns the current authenticated user profile.

Headers:
- `X-Tenant-Slug`
- `Authorization: Bearer <access_token>`

Response:
- `id`
- `email`
- `first_name`
- `last_name`
- `status`
- `locale`
- `role_codes`

## School Management

### `GET /api/v1/schools`

Returns the list of schools for the current tenant.

Headers:
- `X-Tenant-Slug`
- `Authorization: Bearer <access_token>`

### `POST /api/v1/schools`

Creates a new school in the current tenant.

Headers:
- `X-Tenant-Slug`
- `Authorization: Bearer <access_token>`

Request body:
- `name`
- `code`
- `region`
- `district`
- `address`
- `timezone`
- `language_code`
