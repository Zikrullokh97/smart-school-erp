import '../database/local_database.dart';
import 'sync_models.dart';

class SyncQueueRepository {
  const SyncQueueRepository(this._database);

  final LocalDatabase _database;

  Future<void> enqueue(SyncOperationDraft draft) => _database.insertSyncOperation(draft);

  Future<List<SyncQueueItem>> pending({required int limit}) {
    return _database.readPendingSyncOperations(limit: limit);
  }

  Future<void> markApplied(SyncQueueItem item) {
    return _database.updateSyncOperation(
      item.copyWith(status: SyncOperationStatus.applied, lastError: null),
    );
  }

  Future<void> markConflicted(SyncQueueItem item, String reason) {
    return _database.updateSyncOperation(
      item.copyWith(status: SyncOperationStatus.conflicted, lastError: reason),
    );
  }

  Future<void> markFailed(SyncQueueItem item, String error) {
    return _database.updateSyncOperation(
      item.copyWith(
        status: SyncOperationStatus.failed,
        attempts: item.attempts + 1,
        lastError: error,
      ),
    );
  }
}
