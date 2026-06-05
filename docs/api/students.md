# Student API Documentation

## Overview

Student APIs support tenant-scoped student lifecycle management, including student listing, retrieval, creation, and updates.

All requests require the `X-Tenant-Slug` header to resolve the current tenant context.

## Endpoints

### GET /api/v1/students

Returns a list of students for the current tenant.

Permissions

- `students.read`

Response

- `200 OK` with an array of `StudentRead` objects.

### GET /api/v1/students/{student_id}

Returns a specific student by ID.

Permissions

- `students.read`

Response

- `200 OK` with a `StudentRead` object
- `404 Not Found` when the student does not exist in the current tenant

### POST /api/v1/students

Creates a new student record.

Permissions

- `students.manage`

Request body

- `school_id`: UUID of the tenant school where the student is enrolled
- `student_number`: Unique student identifier within the school
- `first_name`, `last_name`, `date_of_birth`, `gender`, `enrollment_date`
- `status`: Student status, defaults to `active`
- `profile`: Free-form JSON object for optional metadata

Response

- `201 Created` with the created `StudentRead` object
- `404 Not Found` when the school is unknown or outside the tenant

### PATCH /api/v1/students/{student_id}

Updates an existing student record.

Permissions

- `students.manage`

Request body

- Any subset of student fields may be updated using the same data shape as creation.

Response

- `200 OK` with the updated `StudentRead` object
- `404 Not Found` when the student does not exist in the current tenant

## StudentRead Schema

- `id`: UUID
- `school_id`: UUID
- `student_number`: string
- `first_name`: string
- `last_name`: string
- `middle_name`: string | null
- `date_of_birth`: date
- `gender`: string
- `status`: string
- `enrollment_date`: date
- `profile`: object
- `created_at`: datetime
- `updated_at`: datetime
