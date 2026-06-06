import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/models/attendance.dart';
import '../data/attendance_repository.dart';

class AttendanceScreen extends ConsumerStatefulWidget {
  const AttendanceScreen({super.key});

  @override
  ConsumerState<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends ConsumerState<AttendanceScreen> {
  final _sessionController = TextEditingController();
  final _studentController = TextEditingController();
  final _notesController = TextEditingController();
  AttendanceCaptureMethod _method = AttendanceCaptureMethod.faceId;
  double _confidence = 0.86;
  bool _saving = false;

  @override
  void dispose() {
    _sessionController.dispose();
    _studentController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final fraudScore = _riskScore;
    final highRisk = fraudScore >= 0.6;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            for (final method in AttendanceCaptureMethod.values)
              ChoiceChip(
                selected: _method == method,
                avatar: Icon(_iconFor(method), size: 18),
                label: Text(method.label),
                onSelected: (_) => setState(() => _method = method),
              ),
          ],
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _sessionController,
          decoration: const InputDecoration(
            labelText: 'Attendance session ID',
            prefixIcon: Icon(Icons.event_available),
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _studentController,
          decoration: const InputDecoration(
            labelText: 'Student ID',
            prefixIcon: Icon(Icons.person_search),
          ),
        ),
        const SizedBox(height: 16),
        Text('Confidence ${(100 * _confidence).round()}%', style: theme.textTheme.labelLarge),
        Slider(
          value: _confidence,
          min: 0,
          max: 1,
          divisions: 20,
          label: '${(100 * _confidence).round()}%',
          onChanged: (value) => setState(() => _confidence = value),
        ),
        TextField(
          controller: _notesController,
          decoration: const InputDecoration(
            labelText: 'Audit notes',
            prefixIcon: Icon(Icons.notes),
          ),
          minLines: 2,
          maxLines: 4,
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Audit information', style: theme.textTheme.titleMedium),
                const SizedBox(height: 12),
                _AuditRow(label: 'Method', value: _method.label),
                _AuditRow(label: 'Source', value: _method.apiValue),
                _AuditRow(label: 'Fraud risk score', value: fraudScore.toStringAsFixed(2)),
                _AuditRow(label: 'Risk state', value: highRisk ? 'Review' : 'Normal'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: _saving ? null : _queueCapture,
          icon: _saving
              ? const SizedBox.square(
                  dimension: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.playlist_add_check),
          label: const Text('Queue attendance'),
        ),
      ],
    );
  }

  double get _riskScore {
    final methodPenalty = switch (_method) {
      AttendanceCaptureMethod.faceId => 0.05,
      AttendanceCaptureMethod.qrCode => 0.20,
      AttendanceCaptureMethod.nfc => 0.16,
      AttendanceCaptureMethod.manual => 0.62,
    };
    final confidencePenalty = (1 - _confidence) * 0.45;
    return (methodPenalty + confidencePenalty).clamp(0.0, 1.0);
  }

  IconData _iconFor(AttendanceCaptureMethod method) {
    return switch (method) {
      AttendanceCaptureMethod.faceId => Icons.face,
      AttendanceCaptureMethod.qrCode => Icons.qr_code_scanner,
      AttendanceCaptureMethod.nfc => Icons.nfc,
      AttendanceCaptureMethod.manual => Icons.edit_note,
    };
  }

  Future<void> _queueCapture() async {
    if (_sessionController.text.trim().isEmpty || _studentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session and student are required.')),
      );
      return;
    }
    setState(() => _saving = true);
    try {
      final operationId = await ref.read(attendanceRepositoryProvider).queueCapture(
            sessionId: _sessionController.text.trim(),
            studentId: _studentController.text.trim(),
            method: _method,
            confidenceScore: _confidence,
            notes: _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Queued operation $operationId')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }
}

class _AuditRow extends StatelessWidget {
  const _AuditRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(child: Text(label)),
          Text(value, style: Theme.of(context).textTheme.labelLarge),
        ],
      ),
    );
  }
}
