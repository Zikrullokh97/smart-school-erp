import '../../../core/network/api_client.dart';
import '../../../core/security/token_store.dart';
import '../../../shared/models/user_session.dart';

class AuthRepository {
  const AuthRepository({required ApiClient apiClient, required TokenStore tokenStore})
      : _apiClient = apiClient,
        _tokenStore = tokenStore;

  final ApiClient _apiClient;
  final TokenStore _tokenStore;

  Future<UserSession> login({
    required String tenantSlug,
    required String email,
    required String password,
  }) async {
    final tokenResponse = await _apiClient.postMap(
      '/auth/token',
      {
        'email': email,
        'password': password,
      },
      tenantSlugOverride: tenantSlug,
    );
    final accessToken = tokenResponse['access_token'] as String;
    final userResponse = await _apiClient.getMap(
      '/auth/me',
      tenantSlugOverride: tenantSlug,
      accessTokenOverride: accessToken,
    );
    final session = UserSession(
      tenantSlug: tenantSlug,
      accessToken: accessToken,
      refreshToken: tokenResponse['refresh_token'] as String,
      expiresIn: tokenResponse['expires_in'] as int,
      user: CurrentUser.fromJson(userResponse),
    );
    await _tokenStore.saveSession(session);
    return session;
  }

  Future<void> logout() => _tokenStore.clear();
}
