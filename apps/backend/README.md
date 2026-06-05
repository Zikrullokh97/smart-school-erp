# Backend App

The backend app contains the FastAPI service for Smart School Cloud ERP.

## Planned Responsibilities

- Tenant-aware API endpoints and service layer.
- SQLAlchemy models and Alembic migrations.
- Authentication, authorization, audit logs, and security controls.
- Domain modules for schools, users, students, teachers, parents, attendance, notifications, scheduling, AI reporting, and offline sync.
- Event outbox, WebSocket notification gateway, and observability instrumentation.

## Technology Direction

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL with TimescaleDB and PGVector extensions
- Redis
- Pytest

## Phase 2 Database Foundation

The backend currently includes:

- SQLAlchemy typed ORM metadata for the core platform schema.
- Alembic configuration and the initial PostgreSQL migration.
- Seed data definitions for platform permissions and system roles.
- Pytest coverage for metadata conventions, PostgreSQL DDL compilation, migration discovery, and seed consistency.

Run backend tests from the repository root:

```bash
uv run --project apps/backend pytest
```

## Authentication and School Management

The backend serves versioned APIs under `/api/v1`.

Key endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/schools`
- `POST /api/v1/schools`
- `GET /api/v1/students`
- `GET /api/v1/students/{student_id}`
- `POST /api/v1/students`
- `PATCH /api/v1/students/{student_id}`
- `GET /api/v1/teachers`
- `GET /api/v1/teachers/{teacher_id}`
- `POST /api/v1/teachers`
- `PATCH /api/v1/teachers/{teacher_id}`
- `GET /api/v1/parents/`
- `GET /api/v1/parents/{parent_id}`
- `POST /api/v1/parents`
- `PATCH /api/v1/parents/{parent_id}`
- `GET /api/v1/parents/{parent_id}/students`
- `POST /api/v1/parents/{parent_id}/students`
- `DELETE /api/v1/parents/{parent_id}/students/{student_id}`

Tenant context is supplied via the `X-Tenant-Slug` request header.
