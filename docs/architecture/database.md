# Database Architecture

## Scope

Phase 2 establishes the database foundation for the Smart School Cloud ERP backend. The schema is tenant-aware from the first migration and includes records needed by the required product modules.

## Technology

- PostgreSQL is the transactional system of record.
- TimescaleDB is enabled for future time-series attendance and operational metrics.
- PGVector is enabled for face embeddings and semantic AI report retrieval.
- SQLAlchemy typed ORM models define application metadata.
- Alembic migrations define deployment history.

## Core Table Groups

| Group | Tables |
| --- | --- |
| Tenancy | `tenants`, `schools` |
| Identity and RBAC | `users`, `roles`, `permissions`, `role_permissions`, `user_roles` |
| Academic structure | `academic_years`, `terms`, `class_groups`, `class_enrollments` |
| People records | `students`, `teachers`, `parent_profiles`, `parent_student_links` |
| Attendance and biometrics | `attendance_sessions`, `attendance_events`, `face_embeddings` |
| Notifications | `notifications` |
| AI reporting | `ai_reports` |
| Scheduling | `rooms`, `schedule_constraints`, `schedule_slots` |
| Offline sync | `sync_devices`, `sync_operations` |
| Governance | `audit_logs`, `outbox_events` |

## Tenant Isolation Rules

- Every tenant-owned table has a non-null `tenant_id`.
- Tenant-owned uniqueness constraints include tenant scope.
- Tenant-owned tables include tenant query support through indexes or tenant-scoped unique constraints.
- Outbox events, audit logs, sync operations, and notifications carry tenant context because they are security-sensitive operational records.

## Identifier Strategy

All primary records use UUID primary keys. Clients may supply separate idempotency keys or operation IDs for offline and event-driven workflows, but server records retain UUID identifiers.

## Extension Usage

The initial migration enables:

- `vector` for PGVector-backed embeddings.
- `timescaledb` for time-series readiness.

Face ID records store 512-dimensional embeddings. AI report records reserve 1536-dimensional embeddings for semantic report retrieval and source matching.

## Seed Data

The initial seed definitions cover platform permissions and system roles. Permission codes are stable strings designed for service-layer authorization checks and future UI permission rendering.
