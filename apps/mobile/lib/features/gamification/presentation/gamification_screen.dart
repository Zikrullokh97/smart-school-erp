import 'package:flutter/material.dart';

class GamificationScreen extends StatelessWidget {
  const GamificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Student progress', style: theme.textTheme.headlineSmall),
        const SizedBox(height: 12),
        const _ProgressTile(
          icon: Icons.star,
          title: 'XP balance',
          value: 'Sync required',
        ),
        const _ProgressTile(
          icon: Icons.local_fire_department,
          title: 'Streak',
          value: 'Awaiting profile',
        ),
        const _ProgressTile(
          icon: Icons.emoji_events,
          title: 'Badges',
          value: 'No cached badges',
        ),
      ],
    );
  }
}

class _ProgressTile extends StatelessWidget {
  const _ProgressTile({required this.icon, required this.title, required this.value});

  final IconData icon;
  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        trailing: Text(value),
      ),
    );
  }
}
