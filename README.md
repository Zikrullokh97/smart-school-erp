# Smart School Cloud ERP

Smart School Cloud ERP is a multi-tenant SaaS platform for Kyrgyzstan schools. The platform combines school administration, attendance, parent engagement, AI reporting, scheduling, and offline-first mobile workflows in one production-oriented system.

## Product Scope

- Manage schools, users, roles, students, teachers, parents, classes, schedules, attendance, notifications, and reports.
- Support Kyrgyzstan school operations with multi-language readiness for Kyrgyz, Russian, and English interfaces.
- Provide secure tenant isolation, audit trails, RBAC, and compliance-minded operational controls.
- Support tenant-scoped authentication and JWT session management for web and mobile clients.
- Enable offline-first mobile usage for attendance capture and parent-facing workflows.
- Integrate AI features for reporting, summarization, speech processing, and face identification infrastructure.

## Monorepo Layout

| Path | Purpose |
| --- | --- |
| `apps/backend` | FastAPI service, domain modules, SQLAlchemy models, Alembic migrations, API tests |
| `apps/web` | Next.js admin and school staff dashboard |
| `apps/mobile` | Flutter mobile app for teachers, parents, and attendance operators |
| `packages/shared-contracts` | Cross-platform API schemas, event names, and generated client contracts |
| `packages/config` | Shared linting, formatting, and build configuration |
| `infra` | Docker, Kubernetes, observability, and deployment assets |
| `docs` | Architecture, product, API, operations, testing, and progress documentation |
| `tooling` | Repository automation that supports builds, tests, and release gates |
| `tools` | Lightweight scripts used before full workspace toolchains exist |

## Phase Status

The active roadmap is maintained in [ROADMAP.md](ROADMAP.md). Each completed phase has a progress report under `docs/progress`.

## Local Validation

Current validation can be run from the repository root:

```bash
pnpm test
```

The validation checks repository documentation gates, backend linting, and backend database foundation tests. On Windows PowerShell, use `pnpm.cmd test` if script execution policy blocks the PowerShell shim.

## Engineering Principles

- Tenant isolation is enforced in application services and database access patterns.
- Every user-facing feature includes API validation, tests, documentation, and auditability.
- Offline-capable workflows are designed with deterministic sync, idempotency, and conflict resolution.
- Event-driven integrations use durable outbox processing before external side effects.
- Security, observability, and deployment automation are first-class deliverables, not release cleanup.

## Backend Database Foundation

The backend database foundation lives in `apps/backend`. It defines tenant-aware SQLAlchemy models, Alembic migrations, and seed data for permissions and system roles. The first schema migration enables PostgreSQL extensions required by the architecture and creates the core tables used by later feature phases.

## Student Module

Student management APIs are implemented under `/api/v1/students` for tenant-scoped student records, including student listing, retrieval, creation, and updates.

## Teacher Module

Teacher management APIs are implemented under `/api/v1/teachers` for tenant-scoped teacher records, including teacher listing, retrieval, creation, and updates.
