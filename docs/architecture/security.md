# Security Architecture

## Identity

- Access tokens are short-lived JWTs signed with asymmetric keys.
- Refresh tokens are rotated, hashed at rest, tenant-aware, and revocable.
- Service accounts use scoped credentials and separate audit attribution.

## Authorization

- RBAC is tenant-scoped.
- Platform roles and school roles are separate permission domains.
- Permission checks happen in service methods before data access or state changes.
- Sensitive operations require explicit permissions and audit log entries.

## Tenant Boundaries

- Tenant context is required for tenant-owned APIs.
- Database queries include tenant scoping by default.
- Cache keys include tenant identifiers.
- Events include tenant metadata and are processed with tenant context.
- Uploaded files and generated artifacts are partitioned by tenant.

## Data Protection

- Secrets are read from environment or secret stores, never committed.
- Passwords are hashed using memory-hard password hashing.
- Sensitive audit records are immutable from normal application flows.
- Face embeddings and biometric evidence require consent state, retention policy, and restricted permissions.

## API Protection

- Input validation is performed through Pydantic schemas.
- Rate limits protect authentication, sync, notification, and AI endpoints.
- Idempotency keys are required for offline mutation APIs.
- Structured errors avoid leaking internals.

## Observability And Incident Response

- Authentication, permission failures, data export, biometric operations, and administrative changes are logged as security events.
- Metrics include authentication failures, rate-limit decisions, outbox lag, sync conflicts, and notification delivery failures.
- Traces propagate request, tenant, user, and correlation identifiers without exposing secrets.
