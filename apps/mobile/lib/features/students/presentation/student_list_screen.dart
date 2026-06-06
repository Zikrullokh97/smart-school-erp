import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/widgets/empty_state.dart';
import '../data/student_repository.dart';

class StudentListScreen extends ConsumerWidget {
  const StudentListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final students = ref.watch(studentsProvider);
    return students.when(
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.school_outlined,
            title: 'No students',
            message: 'Student records will appear here after sync.',
          );
        }
        return RefreshIndicator(
          onRefresh: () => ref.refresh(studentsProvider.future),
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemBuilder: (context, index) {
              final student = items[index];
              return ListTile(
                leading: CircleAvatar(child: Text(student.firstName.characters.first)),
                title: Text(student.displayName),
                subtitle: Text('${student.studentNumber} • ${student.status}'),
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
        title: 'Students unavailable',
        message: error.toString(),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
    );
  }
}
