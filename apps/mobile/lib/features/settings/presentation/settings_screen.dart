import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/settings_controller.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsControllerProvider);
    final controller = ref.read(settingsControllerProvider.notifier);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        SwitchListTile(
          value: settings.simpleMode,
          onChanged: controller.setSimpleMode,
          title: const Text('Parent Simple Mode'),
          secondary: const Icon(Icons.family_restroom),
        ),
        SwitchListTile(
          value: settings.highContrast,
          onChanged: controller.setHighContrast,
          title: const Text('High contrast'),
          secondary: const Icon(Icons.contrast),
        ),
        SwitchListTile(
          value: settings.largeText,
          onChanged: controller.setLargeText,
          title: const Text('Large text'),
          secondary: const Icon(Icons.format_size),
        ),
        SwitchListTile(
          value: settings.largeButtons,
          onChanged: controller.setLargeButtons,
          title: const Text('Large buttons'),
          secondary: const Icon(Icons.smart_button),
        ),
        SwitchListTile(
          value: settings.backgroundSync,
          onChanged: controller.setBackgroundSync,
          title: const Text('Background sync'),
          secondary: const Icon(Icons.sync),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: () => context.go('/parent-simple'),
          icon: const Icon(Icons.arrow_forward),
          label: const Text('Open parent mode'),
        ),
      ],
    );
  }
}
