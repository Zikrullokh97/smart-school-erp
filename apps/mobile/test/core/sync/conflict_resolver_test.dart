import 'package:flutter_test/flutter_test.dart';
import 'package:smart_school_mobile/core/sync/conflict_resolver.dart';
import 'package:smart_school_mobile/core/sync/sync_models.dart';

void main() {
  const resolver = ConflictResolver();

  test('attendance operations are append-first', () {
    final resolution = resolver.resolve(
      resourceType: 'attendance_event',
      operationType: 'create',
      policy: ConflictPolicy.appendOnly,
      baseRevision: '1',
      serverRevision: '2',
    );

    expect(resolution, ConflictResolution.applyLocal);
  });

  test('profile revision mismatch requires human review', () {
    final resolution = resolver.resolve(
      resourceType: 'student_profile',
      operationType: 'update',
      policy: ConflictPolicy.humanReview,
      baseRevision: '1',
      serverRevision: '2',
    );

    expect(resolution, ConflictResolution.needsHumanReview);
  });

  test('notification read state resolves by latest timestamp', () {
    final resolution = resolver.resolve(
      resourceType: 'notification_read_state',
      operationType: 'update',
      policy: ConflictPolicy.humanReview,
      localUpdatedAt: DateTime.utc(2026, 1, 2),
      serverUpdatedAt: DateTime.utc(2026),
    );

    expect(resolution, ConflictResolution.applyLocal);
  });
}
