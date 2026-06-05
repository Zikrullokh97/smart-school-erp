# Offline Sync API Documentation

## Overview

Offline sync APIs support device registration, operation submission, and conflict resolution for local-first mobile clients.

All requests require the `X-Tenant-Slug` header to resolve the tenant context.

## Endpoints

### POST /api/v1/sync/devices

Registers a new sync device for a tenant user.

Permissions

- `sync.manage`

Request body

- `device_key`: unique device identifier.
- `platform`: client platform name.
- `app_version`: application version string.

Response

- `201 Created` with the created `SyncDeviceRead`.

### GET /api/v1/sync/devices

Returns registered sync devices for the current tenant.

Permissions

- `sync.manage`

Response

- `200 OK` with a list of `SyncDeviceRead` objects.

### POST /api/v1/sync/operations

Submits a sync operation from a local client.

Permissions

- `sync.manage`

Request body

- `device_id`: ID of the registered sync device.
- `operation_id`: client-generated operation ID.
- `resource_type`: resource type affected by the operation.
- `resource_id`: resource UUID of the target resource, if available.
- `operation_type`: operation intent such as `create`, `update`, or `delete`.
- `payload_version`: local payload version number.
- `payload`: operation payload.
- `base_revision`: optional conflict base revision.

Response

- `201 Created` with the created `SyncOperationRead`.

### GET /api/v1/sync/operations

Returns sync operations for the tenant.

Permissions

- `sync.manage`

Query parameters

- `status`: optional operation status filter.

Response

- `200 OK` with a list of `SyncOperationRead` objects.

### POST /api/v1/sync/operations/{operation_id}/resolve

Resolves a sync operation conflict.

Permissions

- `sync.manage`

Request body

- `resolution`: one of `apply`, `reject`, or `conflict`.
- `details`: structured resolution details.

Response

- `200 OK` with the resolved `SyncOperationRead`.
