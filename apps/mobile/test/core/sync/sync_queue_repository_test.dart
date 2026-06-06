import 'package:flutter_test/flutter_test.dart';
import 'package:smart_school_mobile/core/database/local_database.dart';
import 'package:smart_school_mobile/core/sync/sync_models.dart';
import 'package:smart_school_mobile/core/sync/sync_queue_repository.dart';

void main() {
  test('repository marks queued operations as applied', () async {
    final database = _FakeLocalDatabase();
    const draft = SyncOperationDraft(
      operationId: 'operation-1',
      tenantId: 'tenant-a',
      resourceType: 'attendance_event',
      operationType: 'create',
      payloadVersion: 1,
      payload: {'student_id': 'student-1'},
      conflictPolicy: ConflictPolicy.appendOnly,
    );
    final repository = SyncQueueRepository(database);

    await repository.enqueue(draft);
    final pending = await repository.pending(limit: 10);
    await repository.markApplied(pending.single);

    expect(database.items.single.status, SyncOperationStatus.applied);
  });
}

class _FakeLocalDatabase implements LocalDatabase {
  final List<SyncQueueItem> items = [];

  @override
  Future<void> insertSyncOperation(SyncOperationDraft draft) async {
    final now = DateTime.utc(2026);
    items.add(
      SyncQueueItem(
        operationId: draft.operationId,
        tenantId: draft.tenantId,
        deviceId: draft.deviceId,
        resourceType: draft.resourceType,
        resourceId: draft.resourceId,
        operationType: draft.operationType,
        payloadVersion: draft.payloadVersion,
        payload: draft.payload,
        baseRevision: draft.baseRevision,
        status: SyncOperationStatus.pending,
        conflictPolicy: draft.conflictPolicy,
        attempts: 0,
        createdAt: now,
        updatedAt: now,
      ),
    );
  }

  @override
  Future<List<SyncQueueItem>> readPendingSyncOperations({required int limit}) async {
    return items
        .where((item) => item.status == SyncOperationStatus.pending)
        .take(limit)
        .toList();
  }

  @override
  Future<void> updateSyncOperation(SyncQueueItem item) async {
    final index = items.indexWhere((candidate) => candidate.operationId == item.operationId);
    items[index] = item;
  }

  @override
  Future<List<Map<String, Object?>>> readCache(String table) async => const [];

  @override
  Future<void> upsertCache({
    required String table,
    required String id,
    required Map<String, Object?> payload,
    required DateTime updatedAt,
  }) async {}

  @override
  Future<void> close() async {}
}
