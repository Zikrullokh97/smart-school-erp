import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../shared/widgets/metric_card.dart';
import '../../auth/application/auth_controller.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final session = authState.asData?.value;
    final width = MediaQuery.sizeOf(context).width;
    final columns = width >= 1000 ? 3 : width >= 640 ? 2 : 1;

    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  session == null ? 'School operations' : 'Welcome, ${session.user.firstName}',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 4),
                Text(
                  'Attendance, family engagement, and review workflows',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.all(16),
          sliver: SliverGrid.count(
            crossAxisCount: columns,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: width >= 640 ? 2.5 : 2.2,
            children: [
              MetricCard(
                icon: Icons.fact_check,
                label: 'Today attendance',
                value: 'Capture',
                onTap: () => context.go('/attendance'),
              ),
              MetricCard(
                icon: Icons.school,
                label: 'Students',
                value: 'Roster',
                onTap: () => context.go('/students'),
              ),
              MetricCard(
                icon: Icons.badge,
                label: 'Teachers',
                value: 'Staff',
                onTap: () => context.go('/teachers'),
              ),
              MetricCard(
                icon: Icons.psychology_alt,
                label: 'AI review',
                value: 'Queue',
                onTap: () => context.go('/ai-review'),
              ),
              MetricCard(
                icon: Icons.emoji_events,
                label: 'Gamification',
                value: 'Progress',
                onTap: () => context.go('/gamification'),
              ),
              MetricCard(
                icon: Icons.family_restroom,
                label: 'Parent mode',
                value: 'Simple',
                onTap: () => context.go('/parent-simple'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
