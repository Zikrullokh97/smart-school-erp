import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/database/local_database.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/network/api_client.dart';
import '../../../core/providers/core_providers.dart';
import '../../../shared/models/teacher.dart';

final teacherRepositoryProvider = Provider<TeacherRepository>((ref) {
  return TeacherRepository(
    apiClient: ref.watch(apiClientProvider),
    database: ref.watch(localDatabaseProvider),
  );
});

final teachersProvider = FutureProvider<List<Teacher>>((ref) {
  return ref.watch(teacherRepositoryProvider).listTeachers();
});

class TeacherRepository {
  const TeacherRepository({required ApiClient apiClient, required LocalDatabase database})
      : _apiClient = apiClient,
        _database = database;

  final ApiClient _apiClient;
  final LocalDatabase _database;

  Future<List<Teacher>> listTeachers() async {
    try {
      final rows = await _apiClient.getList('/teachers');
      final teachers = rows
          .cast<Map<String, dynamic>>()
          .map(Teacher.fromJson)
          .toList(growable: false);
      for (final row in rows.cast<Map<String, dynamic>>()) {
        await _database.upsertCache(
          table: 'teachers',
          id: row['id'] as String,
          payload: row,
          updatedAt: DateTime.now().toUtc(),
        );
      }
      return teachers;
    } on AppException {
      final cached = await _database.readCache('teachers');
      return cached.map((row) => Teacher.fromJson(Map<String, dynamic>.from(row))).toList();
    }
  }
}
