class AIReport {
  const AIReport({
    required this.id,
    required this.reportType,
    required this.status,
    required this.promptHash,
    required this.inputParameters,
    required this.sourceReferences,
    this.schoolId,
    this.outputSummary,
    this.reviewedAt,
  });

  factory AIReport.fromJson(Map<String, dynamic> json) {
    return AIReport(
      id: json['id'] as String,
      schoolId: json['school_id'] as String?,
      reportType: json['report_type'] as String,
      status: json['status'] as String,
      promptHash: json['prompt_hash'] as String,
      inputParameters: (json['input_parameters'] as Map<String, dynamic>? ?? const {}),
      sourceReferences: (json['source_references'] as Map<String, dynamic>? ?? const {}),
      outputSummary: json['output_summary'] as String?,
      reviewedAt: json['reviewed_at'] == null ? null : DateTime.parse(json['reviewed_at'] as String),
    );
  }

  final String id;
  final String? schoolId;
  final String reportType;
  final String status;
  final String promptHash;
  final Map<String, dynamic> inputParameters;
  final Map<String, dynamic> sourceReferences;
  final String? outputSummary;
  final DateTime? reviewedAt;
}

class AIReviewAction {
  const AIReviewAction({
    required this.id,
    required this.aiReportId,
    required this.decision,
    required this.explainability,
    required this.metadata,
    required this.createdAt,
    this.comment,
  });

  factory AIReviewAction.fromJson(Map<String, dynamic> json) {
    return AIReviewAction(
      id: json['id'] as String,
      aiReportId: json['ai_report_id'] as String,
      decision: json['decision'] as String,
      comment: json['comment'] as String?,
      explainability: (json['explainability'] as Map<String, dynamic>? ?? const {}),
      metadata: (json['metadata'] as Map<String, dynamic>? ?? const {}),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  final String id;
  final String aiReportId;
  final String decision;
  final String? comment;
  final Map<String, dynamic> explainability;
  final Map<String, dynamic> metadata;
  final DateTime createdAt;
}
