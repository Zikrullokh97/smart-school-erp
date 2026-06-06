import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../network/api_client.dart';
import '../security/token_store.dart';

class DeviceRegistrationService {
  DeviceRegistrationService({required ApiClient apiClient, required TokenStore tokenStore})
      : _apiClient = apiClient,
        _tokenStore = tokenStore;

  final ApiClient _apiClient;
  final TokenStore _tokenStore;
  final _uuid = const Uuid();

  Future<String> ensureRegistered({required String appVersion}) async {
    final existingDeviceId = await _tokenStore.readDeviceId();
    if (existingDeviceId != null && existingDeviceId.isNotEmpty) {
      return existingDeviceId;
    }

    var deviceKey = await _tokenStore.readDeviceKey();
    if (deviceKey == null || deviceKey.isEmpty) {
      deviceKey = 'flutter-${defaultTargetPlatform.name}-${_uuid.v4()}';
      await _tokenStore.saveDeviceKey(deviceKey);
    }

    final response = await _apiClient.postMap('/sync/devices', {
      'device_key': deviceKey,
      'platform': defaultTargetPlatform.name,
      'app_version': appVersion,
    });
    final deviceId = response['id'] as String;
    await _tokenStore.saveDeviceId(deviceId);
    return deviceId;
  }
}
