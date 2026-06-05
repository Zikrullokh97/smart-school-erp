# Attendance API Documentation

## Overview

Attendance APIs support tenant-aware session tracking, student presence capture, and attendance event audit trails.

All requests require the `X-Tenant-Slug` header to resolve the current tenant context.

## Endpoints

### GET /api/v1/attendance/sessions

Returns a list of attendance sessions for the current tenant.

Permissions

- `attendance.read`

Response

- `200 OK` with an array of `AttendanceSessionRead` objects.

### GET /api/v1/attendance/sessions/{session_id}

Returns a specific attendance session by ID.

Permissions

- `attendance.read`

Response

- `200 OK` with an `AttendanceSessionRead` object
- `404 Not Found` when the session does not exist for the current tenant

### POST /api/v1/attendance/sessions

Creates a new attendance session for a classroom period.

Permissions

- `attendance.manage`

Request body

- `school_id`: UUID of the school where the session is held
- `class_group_id`: UUID of the class group
- `teacher_id`: Optional UUID of the teacher responsible for the session
- `session_date`: Date of the session
- `period_code`: School period identifier
- `starts_at`, `ends_at`: Optional session times
- `status`: Attendance session status, defaults to `open`

Response

- `201 Created` with the created `AttendanceSessionRead` object
- `404 Not Found` when the school or class group does not exist in the current tenant

### PATCH /api/v1/attendance/sessions/{session_id}

Updates an existing attendance session.

Permissions

- `attendance.manage`

Request body

- Any subset of session fields may be updated.

Response

- `200 OK` with the updated `AttendanceSessionRead` object
- `404 Not Found` when the session does not exist in the current tenant

### GET /api/v1/attendance/events

Returns attendance events for the current tenant. Optionally filter by `session_id`.

Permissions

- `attendance.read`

Response

- `200 OK` with an array of `AttendanceEventRead` objects.

### GET /api/v1/attendance/events/{event_id}

Returns a single attendance event by ID.

Permissions

- `attendance.read`

Response

- `200 OK` with an `AttendanceEventRead` object
- `404 Not Found` when the event does not exist for the current tenant

### POST /api/v1/attendance/capture

Captures an attendance event with multi-factor fallback and fraud evidence.

Permissions

- `attendance.capture`

Request body

- `session_id`: UUID of the attendance session
- `student_id`: UUID of the student
- `face_id_token`: Optional face identification token for biometric capture
- `qr_code_token`: Optional QR code token for fallback capture
- `nfc_tag`: Optional NFC tag identifier for fallback capture
- `manual_confirmation`: Optional boolean to accept manual attendance fallback
- `source`: Primary source indicator for the capture request
- `captured_at`: Timestamp when the event was recorded
- `captured_by_user_id`: Optional UUID of the user who captured the event
- `idempotency_key`: Unique key to prevent duplicate event captures
- `confidence_score`: Optional numeric confidence score
- `evidence`: Optional object with auxiliary capture metadata
- `notes`: Optional text notes

Response

- `201 Created` with the created `AttendanceEventRead` object
- `400 Bad Request` when no valid capture method can be determined
- `404 Not Found` when the session or student does not exist in the current tenant
- `409 Conflict` when an event with the same idempotency key already exists

### POST /api/v1/attendance/events

Creates an attendance event record directly without fallback logic.

Permissions

- `attendance.capture`

Request body

- `session_id`: UUID of the attendance session
- `student_id`: UUID of the student
- `event_type`: Attendance event type (present, absent, late, excused, check_in, check_out)
- `source`: Event source (manual, face_id, import, offline_sync)
- `method`: Attendance capture method (manual, face_id, qr_code, nfc)
- `captured_at`: Timestamp when the event was recorded
- `captured_by_user_id`: Optional UUID of the user who captured the event
- `idempotency_key`: Unique key to prevent duplicate event captures
- `confidence_score`: Optional numeric confidence score
- `evidence`: Optional object with capture metadata
- `notes`: Optional text notes

Response

- `201 Created` with the created `AttendanceEventRead` object
- `404 Not Found` when the session or student does not exist in the current tenant
- `409 Conflict` when an event with the same idempotency key already exists

## Schemas

### AttendanceSessionRead

- `id`: UUID
- `school_id`: UUID
- `class_group_id`: UUID
- `teacher_id`: UUID | null
- `session_date`: date
- `period_code`: string
- `starts_at`: time | null
- `ends_at`: time | null
- `status`: string
- `created_at`: datetime
- `updated_at`: datetime

### AttendanceEventRead

- `id`: UUID
- `session_id`: UUID
- `student_id`: UUID
- `event_type`: string
- `source`: string
- `method`: string
- `captured_at`: datetime
- `captured_by_user_id`: UUID | null
- `idempotency_key`: string
- `fraud_score`: number | null
- `fraud_flags`: object
- `confidence_score`: number | null
- `evidence`: object
- `notes`: string | null
- `created_at`: datetime
- `updated_at`: datetime
