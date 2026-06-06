import 'sync_models.dart';

class ConflictResolver {
  const ConflictResolver();

  ConflictResolution resolve({
    required String resourceType,
    required String operationType,
    required ConflictPolicy policy,
    String? baseRevision,
    String? serverRevision,
    DateTime? localUpdatedAt,
    DateTime? serverUpdatedAt,
  }) {
    if (policy == ConflictPolicy.appendOnly || resourceType == 'attendance_event') {
      return ConflictResolution.applyLocal;
    }

    if (policy == ConflictPolicy.clientWins) {
      return ConflictResolution.applyLocal;
    }

    if (policy == ConflictPolicy.serverWins) {
      return ConflictResolution.keepServer;
    }

    if (resourceType == 'notification_read_state') {
      if (localUpdatedAt == null || serverUpdatedAt == null) {
        return ConflictResolution.keepServer;
      }
      return localUpdatedAt.isAfter(serverUpdatedAt)
          ? ConflictResolution.applyLocal
          : ConflictResolution.keepServer;
    }

    if (baseRevision != null && serverRevision != null && baseRevision == serverRevision) {
      return ConflictResolution.applyLocal;
    }

    return ConflictResolution.needsHumanReview;
  }
}
