# Parent API Documentation

## Overview

Parent APIs support tenant-scoped family engagement and student relationship management. Parent profiles can be created and updated, and links between parents and students represent guardianship relationships.

All requests require the `X-Tenant-Slug` header to resolve the current tenant context.

## Endpoints

### GET /api/v1/parents

Returns a list of parent profiles for the current tenant.

Permissions

- `parents.read`

Response

- `200 OK` with an array of `ParentProfileRead` objects.

### GET /api/v1/parents/{parent_id}

Returns a specific parent profile by ID.

Permissions

- `parents.read`

Response

- `200 OK` with a `ParentProfileRead` object
- `404 Not Found` when the parent profile does not exist in the current tenant

### POST /api/v1/parents

Creates a new parent profile.

Permissions

- `parents.manage`

Request body

- `user_id`: Optional UUID of the linked user account for the parent
- `phone_number`: Contact phone number
- `preferred_language`: User locale code, defaults to `ky-KG`
- `profile`: Free-form JSON object for optional metadata
- `ui_preferences`: JSON object for simple-mode, high-contrast, large-button, voice navigation, and accessibility hints

Response

- `201 Created` with the created `ParentProfileRead` object
- `404 Not Found` when the linked user does not exist in the current tenant

### PATCH /api/v1/parents/{parent_id}

Updates an existing parent profile.

Permissions

- `parents.manage`

Request body

- Any subset of parent profile fields may be updated using the same data shape as creation.

Response

- `200 OK` with the updated `ParentProfileRead` object
- `404 Not Found` when the parent profile does not exist in the current tenant

### GET /api/v1/parents/{parent_id}/students

Returns student relationship links for a parent.

Permissions

- `parents.read`

Response

- `200 OK` with a list of `ParentStudentLinkRead` objects.

### POST /api/v1/parents/{parent_id}/students

Creates a new parent-student relationship link.

Permissions

- `parents.manage`

Request body

- `student_id`: UUID of the student being linked
- `relationship`: Relationship type (for example `mother` or `father`)
- `can_pick_up`: Whether the parent can pick up the student
- `emergency_contact`: Whether the parent is an emergency contact

Response

- `201 Created` with the created `ParentStudentLinkRead` object
- `404 Not Found` when the parent profile or student does not exist in the current tenant

### DELETE /api/v1/parents/{parent_id}/students/{student_id}

Deletes an existing student link from a parent profile.

Permissions

- `parents.manage`

Response

- `204 No Content`
- `404 Not Found` when the relationship does not exist in the current tenant

## ParentProfileRead Schema

- `id`: UUID
- `user_id`: UUID | null
- `phone_number`: string
- `preferred_language`: string
- `profile`: object
- `created_at`: datetime
- `updated_at`: datetime

## ParentStudentLinkRead Schema

- `id`: UUID
- `parent_profile_id`: UUID
- `student_id`: UUID
- `relationship`: string
- `can_pick_up`: boolean
- `emergency_contact`: boolean
- `created_at`: datetime
- `updated_at`: datetime
