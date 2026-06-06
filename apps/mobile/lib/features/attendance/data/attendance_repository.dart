import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../core/network/api_client.dart';
import '../../../core/providers/core_providers.dart';
import '../../../core/security/token_store.dart';
import '../../../core/sync/sync_models.dart';
import '../../../core/sync/sync_queue_repository.dart';
import '../../../shared/models/attendance.dart';

final attendanceRepositoryProvider = Provider<AttendanceRepository>((ref) {
  return AttendanceRepository(
    apiClient: ref.watch(apiClientProvider),
    queueRepository: ref.watch(syncQueueRepositoryProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

class AttendanceRepository {
  AttendanceRepository({
    required ApiClient apiClient,
    required SyncQueueRepository queueRepository,
    required TokenStore tokenStore,
  })  : _apiClient = apiClient,
        _queueRepository = queueRepository,
        _tokenStore = tokenStore;

  final ApiClient _apiClient;
  final SyncQueueRepository _queueRepository;
  final TokenStore _tokenStore;
  final _uuid = const Uuid();

  Future<AttendanceEvent> captureNow({
    required String sessionId,
    required String studentId,
    required AttendanceCaptureMethod method,
    required double confidenceScore,
    String? notes,
  }) async {
    final payload = _buildPayload(
      sessionId: sessionId,
      studentId: studentId,
      method: method,
      confidenceScore: confidenceScore,
      notes: notes,
    );
    final response = await _apiClient.postMap('/attendance/capture', payload);
    return AttendanceEvent.fromJson(response);
  }

  Future<String> queueCapture({
    required String sessionId,
    required String studentId,
    required AttendanceCaptureMethod method,
    required double confidenceScore,
    String? notes,
  }) async {
    final tenantSlug = await _tokenStore.readTenantSlug();
    final deviceId = await _tokenStore.readDeviceId();
    if (tenantSlug == null || tenantSlug.isEmpty) {
      throw StateError('Missing tenant context.');
    }
    final operationId = _uuid.v4();
    await _queueRepository.enqueue(
      SyncOperationDraft(
        operationId: operationId,
        tenantId: tenantSlug,
        deviceId: deviceId,
        resourceType: 'attendance_event',
        operationType: 'create',
        payloadVersion: 1,
        conflictPolicy: ConflictPolicy.appendOnly,
        payload: _buildPayload(
          sessionId: sessionId,
          studentId: studentId,
          method: method,
          confidenceScore: confidenceScore,
          notes: notes,
          idempotencyKey: operationId,
        ),
      ),
    );
    return operationId;
  }

  Map<String, Object?> _buildPayload({
    required String sessionId,
    required String studentId,
    required AttendanceCaptureMethod method,
    required double confidenceScore,
    String? notes,
    String? idempotencyKey,
  }) {
    final key = idempotencyKey ?? _uuid.v4();
    return {
      'session_id': sessionId,
      'student_id': studentId,
      'face_id_token': method == AttendanceCaptureMethod.faceId ? 'mobile-face-capture' : null,
      'qr_code_token': method == AttendanceCaptureMethod.qrCode ? 'mobile-qr-capture' : null,
      'nfc_tag': method == AttendanceCaptureMethod.nfc ? 'mobile-nfc-capture' : null,
      'manual_confirmation': method == AttendanceCaptureMethod.manual,
      'source': method.apiValue,
      'captured_at': DateTime.now().toUtc().toIso8601String(),
      'idempotency_key': key,
      'confidence_score': confidenceScore,
      'notes': notes,
      'evidence': {
        'client': 'smart_school_mobile',
        'capture_method': method.apiValue,
        'offline_ready': true,
      },
    };
  }
}
