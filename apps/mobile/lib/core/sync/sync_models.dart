import 'dart:convert';

enum SyncOperationStatus { pending, applied, conflicted, failed }

enum ConflictPolicy { appendOnly, clientWins, serverWins, humanReview }

enum ConflictResolution { applyLocal, keepServer, needsHumanReview }

class SyncOperationDraft {
  const SyncOperationDraft({
    required this.operationId,
    required this.tenantId,
    required this.resourceType,
    required this.operationType,
    required this.payloadVersion,
    required this.payload,
    required this.conflictPolicy,
    this.deviceId,
    this.resourceId,
    this.baseRevision,
  });

  final String operationId;
  final String tenantId;
  final String? deviceId;
  final String resourceType;
  final String? resourceId;
  final String operationType;
  final int payloadVersion;
  final Map<String, Object?> payload;
  final String? baseRevision;
  final ConflictPolicy conflictPolicy;
}

class SyncQueueItem {
  const SyncQueueItem({
    required this.operationId,
    required this.tenantId,
    required this.resourceType,
    required this.operationType,
    required this.payloadVersion,
    required this.payload,
    required this.status,
    required this.conflictPolicy,
    required this.attempts,
    required this.createdAt,
    required this.updatedAt,
    this.deviceId,
    this.resourceId,
    this.baseRevision,
    this.lastError,
  });

  factory SyncQueueItem.fromDatabase(Map<String, Object?> row) {
    return SyncQueueItem(
      operationId: row['operation_id'] as String,
      tenantId: row['tenant_id'] as String,
      deviceId: row['device_id'] as String?,
      resourceType: row['resource_type'] as String,
      resourceId: row['resource_id'] as String?,
      operationType: row['operation_type'] as String,
      payloadVersion: row['payload_version'] as int,
      payload: jsonDecode(row['payload'] as String) as Map<String, Object?>,
      baseRevision: row['base_revision'] as String?,
      status: SyncOperationStatus.values.byName(row['status'] as String),
      conflictPolicy: ConflictPolicy.values.byName(row['conflict_policy'] as String),
      attempts: row['attempts'] as int,
      lastError: row['last_error'] as String?,
      createdAt: DateTime.parse(row['created_at'] as String),
      updatedAt: DateTime.parse(row['updated_at'] as String),
    );
  }

  final String operationId;
  final String tenantId;
  final String? deviceId;
  final String resourceType;
  final String? resourceId;
  final String operationType;
  final int payloadVersion;
  final Map<String, Object?> payload;
  final String? baseRevision;
  final SyncOperationStatus status;
  final ConflictPolicy conflictPolicy;
  final int attempts;
  final String? lastError;
  final DateTime createdAt;
  final DateTime updatedAt;

  SyncQueueItem copyWith({
    SyncOperationStatus? status,
    int? attempts,
    String? lastError,
    DateTime? updatedAt,
  }) {
    return SyncQueueItem(
      operationId: operationId,
      tenantId: tenantId,
      deviceId: deviceId,
      resourceType: resourceType,
      resourceId: resourceId,
      operationType: operationType,
      payloadVersion: payloadVersion,
      payload: payload,
      baseRevision: baseRevision,
      status: status ?? this.status,
      conflictPolicy: conflictPolicy,
      attempts: attempts ?? this.attempts,
      lastError: lastError,
      createdAt: createdAt,
      updatedAt: updatedAt ?? DateTime.now().toUtc(),
    );
  }

  Map<String, Object?> toDatabase() {
    return {
      'operation_id': operationId,
      'tenant_id': tenantId,
      'device_id': deviceId,
      'resource_type': resourceType,
      'resource_id': resourceId,
      'operation_type': operationType,
      'payload_version': payloadVersion,
      'payload': jsonEncode(payload),
      'base_revision': baseRevision,
      'status': status.name,
      'conflict_policy': conflictPolicy.name,
      'attempts': attempts,
      'last_error': lastError,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Map<String, Object?> toApiPayload(String resolvedDeviceId) {
    return {
      'device_id': deviceId ?? resolvedDeviceId,
      'operation_id': operationId,
      'resource_type': resourceType,
      'resource_id': resourceId,
      'operation_type': operationType,
      'payload_version': payloadVersion,
      'payload': payload,
      'base_revision': baseRevision,
    };
  }
}
