import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/models/ai_review.dart';
import '../../../shared/widgets/empty_state.dart';
import '../data/ai_review_repository.dart';

class AIReviewCenterScreen extends ConsumerWidget {
  const AIReviewCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final queue = ref.watch(aiReviewQueueProvider);
    return queue.when(
      data: (reports) {
        if (reports.isEmpty) {
          return const EmptyState(
            icon: Icons.psychology_alt_outlined,
            title: 'No pending reviews',
            message: 'AI recommendations awaiting approval will appear here.',
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemBuilder: (context, index) => _AIReportCard(report: reports[index]),
          separatorBuilder: (context, index) => const SizedBox(height: 12),
          itemCount: reports.length,
        );
      },
      error: (error, stackTrace) => EmptyState(
        icon: Icons.cloud_off,
        title: 'Review queue unavailable',
        message: error.toString(),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}

class _AIReportCard extends ConsumerStatefulWidget {
  const _AIReportCard({required this.report});

  final AIReport report;

  @override
  ConsumerState<_AIReportCard> createState() => _AIReportCardState();
}

class _AIReportCardState extends ConsumerState<_AIReportCard> {
  final _commentController = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.psychology_alt, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(child: Text(widget.report.reportType, style: theme.textTheme.titleLarge)),
                Chip(label: Text(widget.report.status)),
              ],
            ),
            const SizedBox(height: 12),
            Text(widget.report.outputSummary ?? 'Recommendation pending summary.'),
            const SizedBox(height: 12),
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: const Text('Explainability'),
              children: [
                _KeyValueMap(values: widget.report.inputParameters),
                _KeyValueMap(values: widget.report.sourceReferences),
              ],
            ),
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: const Text('Approval history'),
              children: [
                FutureBuilder(
                  future: ref.read(aiReviewRepositoryProvider).history(widget.report.id),
                  builder: (context, snapshot) {
                    final actions = snapshot.data ?? const <AIReviewAction>[];
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Padding(
                        padding: EdgeInsets.all(12),
                        child: LinearProgressIndicator(),
                      );
                    }
                    if (actions.isEmpty) {
                      return const ListTile(title: Text('No history'));
                    }
                    return Column(
                      children: [
                        for (final action in actions)
                          ListTile(
                            leading: const Icon(Icons.history),
                            title: Text(action.decision),
                            subtitle: Text(action.comment ?? action.createdAt.toIso8601String()),
                          ),
                      ],
                    );
                  },
                ),
              ],
            ),
            TextField(
              controller: _commentController,
              decoration: const InputDecoration(
                labelText: 'Reviewer comment',
                prefixIcon: Icon(Icons.rate_review),
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _DecisionButton(
                  label: 'Approve',
                  icon: Icons.check_circle,
                  submitting: _submitting,
                  onPressed: () => _submit('approve'),
                ),
                _DecisionButton(
                  label: 'Reject',
                  icon: Icons.cancel,
                  submitting: _submitting,
                  onPressed: () => _submit('reject'),
                ),
                _DecisionButton(
                  label: 'Escalate',
                  icon: Icons.priority_high,
                  submitting: _submitting,
                  onPressed: () => _submit('escalate'),
                ),
                _DecisionButton(
                  label: 'Defer',
                  icon: Icons.schedule,
                  submitting: _submitting,
                  onPressed: () => _submit('defer'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit(String decision) async {
    setState(() => _submitting = true);
    try {
      await ref.read(aiReviewRepositoryProvider).submitReview(
            reportId: widget.report.id,
            decision: decision,
            comment: _commentController.text.trim(),
          );
      ref.invalidate(aiReviewQueueProvider);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }
}

class _DecisionButton extends StatelessWidget {
  const _DecisionButton({
    required this.label,
    required this.icon,
    required this.submitting,
    required this.onPressed,
  });

  final String label;
  final IconData icon;
  final bool submitting;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: submitting ? null : onPressed,
      icon: Icon(icon),
      label: Text(label),
    );
  }
}

class _KeyValueMap extends StatelessWidget {
  const _KeyValueMap({required this.values});

  final Map<String, dynamic> values;

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty) {
      return const ListTile(title: Text('No details'));
    }
    return Column(
      children: [
        for (final entry in values.entries)
          ListTile(
            dense: true,
            title: Text(entry.key),
            subtitle: Text(entry.value.toString()),
          ),
      ],
    );
  }
}
