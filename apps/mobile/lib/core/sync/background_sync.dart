import 'dart:async';

import 'sync_service.dart';

class BackgroundSyncCoordinator {
  BackgroundSyncCoordinator({required SyncService syncService, required Duration interval})
      : _syncService = syncService,
        _interval = interval;

  final SyncService _syncService;
  final Duration _interval;
  Timer? _timer;

  void start({required Future<String?> Function() deviceIdReader}) {
    _timer?.cancel();
    _timer = Timer.periodic(_interval, (_) async {
      final deviceId = await deviceIdReader();
      if (deviceId != null && deviceId.isNotEmpty) {
        await _syncService.pushPending(deviceId: deviceId);
      }
    });
  }

  void stop() {
    _timer?.cancel();
    _timer = null;
  }
}
