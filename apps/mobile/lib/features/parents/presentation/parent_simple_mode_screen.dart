import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/accessibility/voice_assistant.dart';
import '../../settings/application/settings_controller.dart';

final voiceAssistantRegistryProvider = Provider<VoiceAssistantRegistry>((ref) {
  final registry = VoiceAssistantRegistry();
  registry
    ..register(
      VoiceAssistantAction(
        intent: 'attendance_report',
        phrases: const ['attendance report', 'show attendance', 'катышуу'],
        handler: () async {},
      ),
    )
    ..register(
      VoiceAssistantAction(
        intent: 'message_teacher',
        phrases: const ['message teacher', 'teacher message', 'мугалим'],
        handler: () async {},
      ),
    );
  return registry;
});

class ParentSimpleModeScreen extends ConsumerWidget {
  const ParentSimpleModeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsControllerProvider);
    ref.watch(voiceAssistantRegistryProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Parent'),
        leading: IconButton(
          onPressed: () => context.go('/dashboard'),
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Back',
        ),
      ),
      body: ListView(
        padding: EdgeInsets.all(settings.largeButtons ? 24 : 16),
        children: [
          Text('Today', style: theme.textTheme.headlineMedium),
          const SizedBox(height: 12),
          _SimpleActionButton(
            icon: Icons.fact_check,
            label: 'Attendance report',
            detail: 'One tap report',
            onTap: () {},
          ),
          _SimpleActionButton(
            icon: Icons.chat_bubble_outline,
            label: 'Message teacher',
            detail: 'Quick replies',
            onTap: () {},
          ),
          _SimpleActionButton(
            icon: Icons.emoji_events,
            label: 'Progress',
            detail: 'Badges and summary',
            onTap: () => context.go('/gamification'),
          ),
          _SimpleActionButton(
            icon: Icons.emergency,
            label: 'Emergency contact',
            detail: 'Call school office',
            onTap: () {},
          ),
          const SizedBox(height: 16),
          SegmentedButton<bool>(
            segments: const [
              ButtonSegment(value: false, label: Text('Standard'), icon: Icon(Icons.text_fields)),
              ButtonSegment(value: true, label: Text('Large'), icon: Icon(Icons.format_size)),
            ],
            selected: {settings.largeText},
            onSelectionChanged: (value) {
              ref.read(settingsControllerProvider.notifier).setLargeText(value.first);
            },
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            value: settings.highContrast,
            onChanged: ref.read(settingsControllerProvider.notifier).setHighContrast,
            title: const Text('High contrast'),
            secondary: const Icon(Icons.contrast),
          ),
        ],
      ),
    );
  }
}

class _SimpleActionButton extends StatelessWidget {
  const _SimpleActionButton({
    required this.icon,
    required this.label,
    required this.detail,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String detail;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: FilledButton(
        onPressed: onTap,
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          alignment: Alignment.centerLeft,
        ),
        child: Row(
          children: [
            Icon(icon, size: 32),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: theme.textTheme.titleLarge?.copyWith(color: Colors.white)),
                  const SizedBox(height: 2),
                  Text(detail, style: theme.textTheme.bodyLarge?.copyWith(color: Colors.white)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
