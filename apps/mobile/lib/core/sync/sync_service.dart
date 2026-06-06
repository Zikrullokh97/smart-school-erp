import '../errors/app_exception.dart';
import '../network/api_client.dart';
import 'conflict_resolver.dart';
import 'sync_models.dart';
import 'sync_queue_repository.dart';

class SyncService {
  const SyncService({
    required ApiClient apiClient,
    required SyncQueueRepository queueRepository,
    required ConflictResolver resolver,
    required int batchSize,
  })  : _apiClient = apiClient,
        _queueRepository = queueRepository,
        _resolver = resolver,
        _batchSize = batchSize;

  final ApiClient _apiClient;
  final SyncQueueRepository _queueRepository;
  final ConflictResolver _resolver;
  final int _batchSize;

  Future<SyncRunResult> pushPending({required String deviceId}) async {
    final pending = await _queueRepository.pending(limit: _batchSize);
    var applied = 0;
    var conflicted = 0;
    var failed = 0;

    for (final item in pending) {
      try {
        await _apiClient.postMap('/sync/operations', item.toApiPayload(deviceId));
        await _queueRepository.markApplied(item);
        applied++;
      } on ConflictException catch (error) {
        final resolution = _resolver.resolve(
          resourceType: item.resourceType,
          operationType: item.operationType,
          policy: item.conflictPolicy,
          baseRevision: item.baseRevision,
          serverRevision: _extractServerRevision(error.details),
        );
        if (resolution == ConflictResolution.needsHumanReview) {
          await _queueRepository.markConflicted(item, error.message);
          conflicted++;
        } else {
          await _queueRepository.markFailed(item, error.message);
          failed++;
        }
      } on AppException catch (error) {
        await _queueRepository.markFailed(item, error.message);
        failed++;
      }
    }

    return SyncRunResult(applied: applied, conflicted: conflicted, failed: failed);
  }

  String? _extractServerRevision(Object? details) {
    if (details is Map<String, dynamic>) {
      final revision = details['server_revision'];
      return revision is String ? revision : null;
    }
    return null;
  }
}

class SyncRunResult {
  const SyncRunResult({required this.applied, required this.conflicted, required this.failed});

  final int applied;
  final int conflicted;
  final int failed;

  bool get hasWork => applied + conflicted + failed > 0;
}
