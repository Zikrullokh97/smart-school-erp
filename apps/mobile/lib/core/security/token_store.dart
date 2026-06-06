import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../shared/models/user_session.dart';

class TokenStore {
  TokenStore({FlutterSecureStorage? secureStorage}) : _secureStorage = secureStorage ?? const FlutterSecureStorage();

  static const _accessTokenKey = 'smart_school.access_token';
  static const _refreshTokenKey = 'smart_school.refresh_token';
  static const _tenantSlugKey = 'smart_school.tenant_slug';
  static const _deviceIdKey = 'smart_school.device_id';
  static const _deviceKeyKey = 'smart_school.device_key';

  final FlutterSecureStorage _secureStorage;

  Future<void> saveSession(UserSession session) async {
    await _secureStorage.write(key: _accessTokenKey, value: session.accessToken);
    await _secureStorage.write(key: _refreshTokenKey, value: session.refreshToken);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tenantSlugKey, session.tenantSlug);
  }

  Future<String?> readAccessToken() => _secureStorage.read(key: _accessTokenKey);

  Future<String?> readRefreshToken() => _secureStorage.read(key: _refreshTokenKey);

  Future<String?> readTenantSlug() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tenantSlugKey);
  }

  Future<void> saveDeviceId(String deviceId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_deviceIdKey, deviceId);
  }

  Future<String?> readDeviceId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_deviceIdKey);
  }

  Future<void> saveDeviceKey(String deviceKey) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_deviceKeyKey, deviceKey);
  }

  Future<String?> readDeviceKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_deviceKeyKey);
  }

  Future<void> clear() async {
    await _secureStorage.delete(key: _accessTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tenantSlugKey);
    await prefs.remove(_deviceIdKey);
  }
}
