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
