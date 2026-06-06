import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/widgets/empty_state.dart';
import '../data/teacher_repository.dart';

class TeacherListScreen extends ConsumerWidget {
  const TeacherListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final teachers = ref.watch(teachersProvider);
    return teachers.when(
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.badge_outlined,
            title: 'No teachers',
            message: 'Teacher records will appear here after sync.',
          );
        }
        return RefreshIndicator(
          onRefresh: () => ref.refresh(teachersProvider.future),
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemBuilder: (context, index) {
              final teacher = items[index];
              return ListTile(
                leading: CircleAvatar(child: Text(teacher.firstName.characters.first)),
                title: Text(teacher.displayName),
                subtitle: Text('${teacher.employeeNumber} • ${teacher.status}'),
                trailing: const Icon(Icons.chevron_right),
              );
            },
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemCount: items.length,
          ),
        );
      },
      error: (error, stackTrace) => EmptyState(
        icon: Icons.cloud_off,
        title: 'Teachers unavailable',
        message: error.toString(),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}
