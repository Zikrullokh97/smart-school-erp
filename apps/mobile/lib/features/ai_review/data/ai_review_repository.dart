import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../core/providers/core_providers.dart';
import '../../../shared/models/ai_review.dart';

final aiReviewRepositoryProvider = Provider<AIReviewRepository>((ref) {
  return AIReviewRepository(ref.watch(apiClientProvider));
});

final aiReviewQueueProvider = FutureProvider<List<AIReport>>((ref) {
  return ref.watch(aiReviewRepositoryProvider).listQueue();
});

class AIReviewRepository {
  const AIReviewRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<List<AIReport>> listQueue() async {
    final rows = await _apiClient.getList('/ai/reports/queue');
    return rows.cast<Map<String, dynamic>>().map(AIReport.fromJson).toList(growable: false);
  }

  Future<List<AIReviewAction>> history(String reportId) async {
    final rows = await _apiClient.getList('/ai/reports/$reportId/history');
    return rows
        .cast<Map<String, dynamic>>()
        .map(AIReviewAction.fromJson)
        .toList(growable: false);
  }

  Future<AIReport> submitReview({
    required String reportId,
    required String decision,
    required String comment,
  }) async {
    final response = await _apiClient.postMap('/ai/reports/$reportId/review', {
      'decision': decision,
      'comment': comment,
      'explainability': {
        'review_surface': 'mobile',
        'human_confirmed': true,
      },
      'metadata': {
        'client': 'smart_school_mobile',
      },
    });
    return AIReport.fromJson(response);
  }
}
