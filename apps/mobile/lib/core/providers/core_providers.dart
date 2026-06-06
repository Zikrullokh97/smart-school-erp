import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../database/local_database.dart';
import '../device/device_registration_service.dart';
import '../network/api_client.dart';
import '../security/token_store.dart';
import '../sync/background_sync.dart';
import '../sync/conflict_resolver.dart';
import '../sync/sync_queue_repository.dart';
import '../sync/sync_service.dart';

final appConfigProvider = Provider<AppConfig>((ref) => AppConfig.fromEnvironment());

final httpClientProvider = Provider<http.Client>((ref) {
  final client = http.Client();
  ref.onDispose(client.close);
  return client;
});

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());

final apiClientProvider = Provider<ApiClient>((ref) {
  final tokenStore = ref.watch(tokenStoreProvider);
  return ApiClient(
    config: ref.watch(appConfigProvider),
    httpClient: ref.watch(httpClientProvider),
    accessTokenReader: tokenStore.readAccessToken,
    tenantSlugReader: tokenStore.readTenantSlug,
  );
});

final localDatabaseProvider = Provider<LocalDatabase>((ref) {
  final database = SqfliteLocalDatabase();
  ref.onDispose(database.close);
  return database;
});

final conflictResolverProvider = Provider<ConflictResolver>((ref) => const ConflictResolver());

final syncQueueRepositoryProvider = Provider<SyncQueueRepository>((ref) {
  return SyncQueueRepository(ref.watch(localDatabaseProvider));
});

final syncServiceProvider = Provider<SyncService>((ref) {
  return SyncService(
    apiClient: ref.watch(apiClientProvider),
    queueRepository: ref.watch(syncQueueRepositoryProvider),
    resolver: ref.watch(conflictResolverProvider),
    batchSize: ref.watch(appConfigProvider).syncBatchSize,
  );
});

final deviceRegistrationServiceProvider = Provider<DeviceRegistrationService>((ref) {
  return DeviceRegistrationService(
    apiClient: ref.watch(apiClientProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

final backgroundSyncCoordinatorProvider = Provider<BackgroundSyncCoordinator>((ref) {
  return BackgroundSyncCoordinator(
    syncService: ref.watch(syncServiceProvider),
    interval: Duration(seconds: ref.watch(appConfigProvider).backgroundSyncIntervalSeconds),
  );
});
