# Offline Synchronization Architecture

## Design Goals

- Allow teachers and attendance operators to capture critical school data during unreliable connectivity.
- Preserve tenant isolation and user permissions during sync.
- Make repeated client submissions safe through idempotency.
- Resolve conflicts deterministically and surface reviewable exceptions.

## Client Model

The mobile app stores a local operation queue. Each operation includes:

- Client-generated operation ID.
- Tenant ID and actor ID.
- Resource type and resource ID when known.
- Operation type.
- Payload version.
- Local timestamp and device ID.
- Last known server revision for conflict detection.

## Server Model

The backend accepts sync batches through authenticated tenant-scoped endpoints. The server validates permissions, applies operations in deterministic order, records accepted operation IDs, and returns updated resource revisions.

## Conflict Policy

- Attendance capture is append-first and correction-based.
- Profile updates use revision checks and return conflicts when both client and server changed the same field family.
- Notification read state uses last-write-wins by server receive time because it is low risk.
- Biometric evidence sync is append-only and bound to consent status at processing time.

## Reliability

Sync endpoints are idempotent. Durable outbox events notify read-model and WebSocket consumers after committed changes.
