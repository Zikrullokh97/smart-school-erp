# Teacher API Documentation

## Overview

Teacher APIs support tenant-scoped teacher lifecycle management, including teacher listing, retrieval, creation, and updates.

All requests require the `X-Tenant-Slug` header to resolve the current tenant context.

## Endpoints

### GET /api/v1/teachers

Returns a list of teachers for the current tenant.

Permissions

- `teachers.read`

Response

- `200 OK` with an array of `TeacherRead` objects.

### GET /api/v1/teachers/{teacher_id}

Returns a specific teacher by ID.

Permissions

- `teachers.read`

Response

- `200 OK` with a `TeacherRead` object
- `404 Not Found` when the teacher does not exist in the current tenant

### POST /api/v1/teachers

Creates a new teacher record.

Permissions

- `teachers.manage`

Request body

- `school_id`: UUID of the tenant school where the teacher is assigned
- `user_id`: Optional UUID of the linked user account for the teacher
- `employee_number`: Unique teacher identifier within the school
- `first_name`, `last_name`, `hire_date`
- `status`: Teacher status, defaults to `active`
- `profile`: Free-form JSON object for optional metadata

Response

- `201 Created` with the created `TeacherRead` object
- `404 Not Found` when the school or user is unknown or outside the tenant

### PATCH /api/v1/teachers/{teacher_id}

Updates an existing teacher record.

Permissions

- `teachers.manage`

Request body

- Any subset of teacher fields may be updated using the same data shape as creation.

Response

- `200 OK` with the updated `TeacherRead` object
- `404 Not Found` when the teacher does not exist in the current tenant

## TeacherRead Schema

- `id`: UUID
- `school_id`: UUID
- `user_id`: UUID | null
- `employee_number`: string
- `first_name`: string
- `last_name`: string
- `hire_date`: date
- `status`: string
- `profile`: object
- `created_at`: datetime
- `updated_at`: datetime
