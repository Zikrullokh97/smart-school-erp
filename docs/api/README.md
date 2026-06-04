# API Documentation

API specifications will be generated from FastAPI OpenAPI schemas and documented here as backend modules are implemented.

## Standards

- All APIs are versioned under `/api/v1`.
- Tenant-owned APIs require tenant context.
- Mutating offline-capable APIs support idempotency keys.
- Errors use a consistent structured response shape.
- Authentication, authorization, validation, and audit behavior are documented with each module.
