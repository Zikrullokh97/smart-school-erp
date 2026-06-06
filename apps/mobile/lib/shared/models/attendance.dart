enum AttendanceCaptureMethod { faceId, qrCode, nfc, manual }

extension AttendanceCaptureMethodLabel on AttendanceCaptureMethod {
  String get apiValue {
    return switch (this) {
      AttendanceCaptureMethod.faceId => 'face_id',
      AttendanceCaptureMethod.qrCode => 'qr_code',
      AttendanceCaptureMethod.nfc => 'nfc',
      AttendanceCaptureMethod.manual => 'manual',
    };
  }

  String get label {
    return switch (this) {
      AttendanceCaptureMethod.faceId => 'Face ID',
      AttendanceCaptureMethod.qrCode => 'QR Code',
      AttendanceCaptureMethod.nfc => 'NFC',
      AttendanceCaptureMethod.manual => 'Manual',
    };
  }
}

class AttendanceEvent {
  const AttendanceEvent({
    required this.id,
    required this.sessionId,
    required this.studentId,
    required this.eventType,
    required this.source,
    required this.method,
    required this.capturedAt,
    required this.idempotencyKey,
    required this.fraudFlags,
    required this.evidence,
    this.capturedByUserId,
    this.fraudScore,
    this.confidenceScore,
    this.notes,
  });

  factory AttendanceEvent.fromJson(Map<String, dynamic> json) {
    return AttendanceEvent(
      id: json['id'] as String,
      sessionId: json['session_id'] as String,
      studentId: json['student_id'] as String,
      eventType: json['event_type'] as String,
      source: json['source'] as String,
      method: json['method'] as String,
      capturedAt: DateTime.parse(json['captured_at'] as String),
      capturedByUserId: json['captured_by_user_id'] as String?,
      idempotencyKey: json['idempotency_key'] as String,
      fraudScore: (json['fraud_score'] as num?)?.toDouble(),
      fraudFlags: (json['fraud_flags'] as Map<String, dynamic>? ?? const {}),
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      evidence: (json['evidence'] as Map<String, dynamic>? ?? const {}),
      notes: json['notes'] as String?,
    );
  }

  final String id;
  final String sessionId;
  final String studentId;
  final String eventType;
  final String source;
  final String method;
  final DateTime capturedAt;
  final String? capturedByUserId;
  final String idempotencyKey;
  final double? fraudScore;
  final Map<String, dynamic> fraudFlags;
  final double? confidenceScore;
  final Map<String, dynamic> evidence;
  final String? notes;
}
