import 'dart:convert';

import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';

import '../sync/sync_models.dart';

abstract class LocalDatabase {
  Future<void> upsertCache({
    required String table,
    required String id,
    required Map<String, Object?> payload,
    required DateTime updatedAt,
  });

  Future<List<Map<String, Object?>>> readCache(String table);

  Future<void> insertSyncOperation(SyncOperationDraft draft);

  Future<List<SyncQueueItem>> readPendingSyncOperations({required int limit});

  Future<void> updateSyncOperation(SyncQueueItem item);

  Future<void> close();
}

class SqfliteLocalDatabase implements LocalDatabase {
  Database? _database;

  Future<Database> get _db async => _database ??= await _open();

  Future<Database> _open() async {
    final databasePath = await getDatabasesPath();
    final path = p.join(databasePath, 'smart_school_mobile.db');
    return openDatabase(path, version: 1, onCreate: _createSchema);
  }

  Future<void> _createSchema(Database db, int version) async {
    await db.execute('''
CREATE TABLE cached_records (
  table_name TEXT NOT NULL,
  id TEXT NOT NULL,
  payload TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (table_name, id)
)
''');
    await db.execute('''
CREATE TABLE sync_queue (
  operation_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  device_id TEXT,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  operation_type TEXT NOT NULL,
  payload_version INTEGER NOT NULL,
  payload TEXT NOT NULL,
  base_revision TEXT,
  status TEXT NOT NULL,
  conflict_policy TEXT NOT NULL,
  attempts INTEGER NOT NULL,
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
''');
    await db.execute('CREATE INDEX ix_sync_queue_status ON sync_queue(status)');
  }

  @override
  Future<void> upsertCache({
    required String table,
    required String id,
    required Map<String, Object?> payload,
    required DateTime updatedAt,
  }) async {
    final db = await _db;
    await db.insert('cached_records', {
      'table_name': table,
      'id': id,
      'payload': jsonEncode(payload),
      'updated_at': updatedAt.toIso8601String(),
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  @override
  Future<List<Map<String, Object?>>> readCache(String table) async {
    final db = await _db;
    final rows = await db.query(
      'cached_records',
      where: 'table_name = ?',
      whereArgs: [table],
      orderBy: 'updated_at DESC',
    );
    return rows
        .map((row) => jsonDecode(row['payload'] as String) as Map<String, Object?>)
        .toList(growable: false);
  }

  @override
  Future<void> insertSyncOperation(SyncOperationDraft draft) async {
    final now = DateTime.now().toUtc();
    final db = await _db;
    await db.insert('sync_queue', {
      'operation_id': draft.operationId,
      'tenant_id': draft.tenantId,
      'device_id': draft.deviceId,
      'resource_type': draft.resourceType,
      'resource_id': draft.resourceId,
      'operation_type': draft.operationType,
      'payload_version': draft.payloadVersion,
      'payload': jsonEncode(draft.payload),
      'base_revision': draft.baseRevision,
      'status': SyncOperationStatus.pending.name,
      'conflict_policy': draft.conflictPolicy.name,
      'attempts': 0,
      'last_error': null,
      'created_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  @override
  Future<List<SyncQueueItem>> readPendingSyncOperations({required int limit}) async {
    final db = await _db;
    final rows = await db.query(
      'sync_queue',
      where: 'status IN (?, ?)',
      whereArgs: [SyncOperationStatus.pending.name, SyncOperationStatus.failed.name],
      orderBy: 'created_at ASC',
      limit: limit,
    );
    return rows.map(SyncQueueItem.fromDatabase).toList(growable: false);
  }

  @override
  Future<void> updateSyncOperation(SyncQueueItem item) async {
    final db = await _db;
    await db.update(
      'sync_queue',
      item.toDatabase(),
      where: 'operation_id = ?',
      whereArgs: [item.operationId],
    );
  }

  @override
  Future<void> close() async {
    final database = _database;
    if (database != null) {
      await database.close();
      _database = null;
    }
  }
}
