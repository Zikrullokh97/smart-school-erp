class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.syncBatchSize,
    required this.backgroundSyncIntervalSeconds,
  });

  factory AppConfig.fromEnvironment() {
    return const AppConfig(
      apiBaseUrl: String.fromEnvironment(
        'SMART_SCHOOL_API_BASE_URL',
        defaultValue: 'http://10.0.2.2:8000/api/v1',
      ),
      syncBatchSize: int.fromEnvironment('SMART_SCHOOL_SYNC_BATCH_SIZE', defaultValue: 25),
      backgroundSyncIntervalSeconds: int.fromEnvironment(
        'SMART_SCHOOL_BACKGROUND_SYNC_SECONDS',
        defaultValue: 60,
      ),
    );
  }

  final String apiBaseUrl;
  final int syncBatchSize;
  final int backgroundSyncIntervalSeconds;

  Uri resolve(String path, [Map<String, String?> queryParameters = const {}]) {
    final normalizedBase = apiBaseUrl.endsWith('/') ? apiBaseUrl : '$apiBaseUrl/';
    final normalizedPath = path.startsWith('/') ? path.substring(1) : path;
    final uri = Uri.parse(normalizedBase).resolve(normalizedPath);
    final query = <String, String>{};
    for (final entry in queryParameters.entries) {
      if (entry.value != null && entry.value!.isNotEmpty) {
        query[entry.key] = entry.value!;
      }
    }
    return query.isEmpty ? uri : uri.replace(queryParameters: query);
  }
}
