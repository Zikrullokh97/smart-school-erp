# AGENTS.md

These instructions guide autonomous engineering work in this repository.

## Mission

Build Smart School Cloud ERP as a production-ready multi-tenant SaaS platform for Kyrgyzstan schools using FastAPI, PostgreSQL, Redis, TimescaleDB, PGVector, Next.js, Flutter, Docker, Kubernetes, GitHub Actions, and AI integrations.

## Required Working Pattern

1. Work in roadmap order unless a production blocker requires an earlier supporting change.
2. Finish one phase before starting the next phase.
3. For every phase, implement code, validation, tests, documentation, and a progress report.
4. Run the relevant tests before committing a phase.
5. Keep `ROADMAP.md` and `docs/progress` updated after every milestone.
6. Commit each completed phase with a clear message.

## Quality Bar

- Do not add knowingly incomplete implementations, unresolved task comments, or partial flows.
- Prefer scalable enterprise-grade choices when requirements leave room for interpretation.
- Keep tenant boundaries explicit in models, queries, service methods, events, cache keys, and storage paths.
- Add automated tests for each module and failure mode introduced by a change.
- Document APIs, operations, security decisions, and deployment steps as part of the change that introduces them.

## Architecture Defaults

- Backend uses FastAPI with SQLAlchemy 2.x typed ORM models, Alembic migrations, Pydantic validation, JWT authentication, structured logging, and OpenTelemetry hooks.
- PostgreSQL is the system of record. TimescaleDB is used for time-series attendance and telemetry where it provides operational value. PGVector is used for AI search and semantic reporting features.
- Redis is used for caching, rate limiting, WebSocket fan-out coordination, background job coordination, and short-lived sync state.
- Domain writes emit durable outbox events in the same database transaction as state changes.
- RBAC uses tenant-scoped roles, permission grants, and least-privilege defaults.
- Offline-first features use client-generated operation IDs, idempotent APIs, revision tokens, and deterministic conflict policies.
- Frontend uses Next.js, TypeScript, TailwindCSS, shadcn/ui, and generated API clients.
- Mobile uses Flutter with local persistence, sync queues, encrypted storage for secrets, and TFLite for on-device inference where appropriate.

## Documentation Expectations

- Architecture decisions live in `docs/architecture/adr`.
- Phase reports live in `docs/progress`.
- API specifications live in `docs/api`.
- Operations guidance lives in `docs/operations`.
- Testing strategy and evidence live in `docs/testing`.

## Definition of Done

A phase is complete only when tests pass, documentation is updated, `ROADMAP.md` reflects progress, and the phase has been committed.
