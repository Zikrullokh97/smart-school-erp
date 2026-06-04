# Testing Strategy

## Test Layers

- Unit tests validate domain rules, permission decisions, schema validation, sync policies, and utility behavior.
- Integration tests validate FastAPI endpoints, database migrations, repository queries, Redis-backed flows, and outbox processing.
- Contract tests validate generated clients against OpenAPI schemas.
- Frontend tests validate critical dashboard workflows and permission-driven rendering.
- Mobile tests validate offline queue behavior, conflict handling, local persistence, and API sync contracts.
- E2E tests validate core school workflows across web, backend, and database.
- Infrastructure tests validate Docker builds, CI workflows, Kubernetes manifests, health checks, and deployment readiness.

## Phase 1 Validation

Phase 1 uses a repository validation script because the product code has not been introduced yet. Later phases will extend the test suite with runtime-specific tests.

## Minimum Evidence Per Phase

Each progress report records:

- Test command.
- Test result.
- Documentation changed.
- Commit reference after commit completion.
- Known risks or follow-up areas for later phases.
