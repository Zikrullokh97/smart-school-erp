import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/database/local_database.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/network/api_client.dart';
import '../../../core/providers/core_providers.dart';
import '../../../shared/models/student.dart';

final studentRepositoryProvider = Provider<StudentRepository>((ref) {
  return StudentRepository(
    apiClient: ref.watch(apiClientProvider),
    database: ref.watch(localDatabaseProvider),
  );
});

final studentsProvider = FutureProvider<List<Student>>((ref) {
  return ref.watch(studentRepositoryProvider).listStudents();
});

class StudentRepository {
  const StudentRepository({required ApiClient apiClient, required LocalDatabase database})
      : _apiClient = apiClient,
        _database = database;

  final ApiClient _apiClient;
  final LocalDatabase _database;

  Future<List<Student>> listStudents() async {
    try {
      final rows = await _apiClient.getList('/students');
      final students = rows
          .cast<Map<String, dynamic>>()
          .map(Student.fromJson)
          .toList(growable: false);
      for (final row in rows.cast<Map<String, dynamic>>()) {
        await _database.upsertCache(
          table: 'students',
          id: row['id'] as String,
          payload: row,
          updatedAt: DateTime.now().toUtc(),
        );
      }
      return students;
    } on AppException {
      final cached = await _database.readCache('students');
      return cached.map((row) => Student.fromJson(Map<String, dynamic>.from(row))).toList();
    }
  }
}
