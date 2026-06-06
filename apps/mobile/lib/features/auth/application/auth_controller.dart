import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../shared/models/user_session.dart';
import '../data/auth_repository.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    apiClient: ref.watch(apiClientProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

final authControllerProvider = NotifierProvider<AuthController, AsyncValue<UserSession?>>(() {
  return AuthController();
});

class AuthController extends Notifier<AsyncValue<UserSession?>> {
  late final AuthRepository _repository;

  @override
  AsyncValue<UserSession?> build() {
    _repository = ref.watch(authRepositoryProvider);
    return const AsyncValue.data(null);
  }

  Future<void> login({
    required String tenantSlug,
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard<UserSession?>(() async {
      return await _repository.login(
        tenantSlug: tenantSlug,
        email: email,
        password: password,
      );
    });
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AsyncValue.data(null);
  }
}
