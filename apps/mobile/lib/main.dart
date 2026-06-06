import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/app_theme.dart';
import 'features/settings/application/settings_controller.dart';
import 'router/app_router.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: SmartSchoolMobileApp()));
}

class SmartSchoolMobileApp extends ConsumerWidget {
  const SmartSchoolMobileApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final settings = ref.watch(settingsControllerProvider);

    return MaterialApp.router(
      title: 'Smart School',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(settings),
      darkTheme: AppTheme.dark(settings),
      highContrastTheme: AppTheme.highContrast(settings),
      themeMode: settings.highContrast ? ThemeMode.dark : ThemeMode.light,
      routerConfig: router,
    );
  }
}
