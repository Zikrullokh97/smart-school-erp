import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../errors/app_exception.dart';

typedef TokenReader = Future<String?> Function();
typedef TenantSlugReader = Future<String?> Function();

class ApiClient {
  ApiClient({
    required AppConfig config,
    required http.Client httpClient,
    required TokenReader accessTokenReader,
    required TenantSlugReader tenantSlugReader,
  })  : _config = config,
        _httpClient = httpClient,
        _accessTokenReader = accessTokenReader,
        _tenantSlugReader = tenantSlugReader;

  final AppConfig _config;
  final http.Client _httpClient;
  final TokenReader _accessTokenReader;
  final TenantSlugReader _tenantSlugReader;

  Future<List<dynamic>> getList(
    String path, {
    Map<String, String?> query = const {},
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final body = await _send(
      'GET',
      path,
      query: query,
      tenantSlugOverride: tenantSlugOverride,
      accessTokenOverride: accessTokenOverride,
    );
    if (body is List<dynamic>) {
      return body;
    }
    throw const AppException('Expected a list response from the server.');
  }

  Future<Map<String, dynamic>> getMap(
    String path, {
    Map<String, String?> query = const {},
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final body = await _send(
      'GET',
      path,
      query: query,
      tenantSlugOverride: tenantSlugOverride,
      accessTokenOverride: accessTokenOverride,
    );
    if (body is Map<String, dynamic>) {
      return body;
    }
    throw const AppException('Expected an object response from the server.');
  }

  Future<Map<String, dynamic>> postMap(
    String path,
    Map<String, Object?> payload, {
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final body = await _send(
      'POST',
      path,
      body: payload,
      tenantSlugOverride: tenantSlugOverride,
      accessTokenOverride: accessTokenOverride,
    );
    if (body is Map<String, dynamic>) {
      return body;
    }
    throw const AppException('Expected an object response from the server.');
  }

  Future<Map<String, dynamic>> patchMap(
    String path,
    Map<String, Object?> payload, {
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final body = await _send(
      'PATCH',
      path,
      body: payload,
      tenantSlugOverride: tenantSlugOverride,
      accessTokenOverride: accessTokenOverride,
    );
    if (body is Map<String, dynamic>) {
      return body;
    }
    throw const AppException('Expected an object response from the server.');
  }

  Future<dynamic> _send(
    String method,
    String path, {
    Map<String, String?> query = const {},
    Map<String, Object?>? body,
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final uri = _config.resolve(path, query);
    final headers = await _headers(
      tenantSlugOverride: tenantSlugOverride,
      accessTokenOverride: accessTokenOverride,
    );
    final encodedBody = body == null ? null : jsonEncode(body);

    late http.Response response;
    try {
      response = await _httpClient
          .send(
            http.Request(method, uri)
              ..headers.addAll(headers)
              ..body = encodedBody ?? '',
          )
          .then(http.Response.fromStream)
          .timeout(const Duration(seconds: 20));
    } on TimeoutException catch (error) {
      throw AppException('Request timed out.', details: error);
    } on http.ClientException catch (error) {
      throw AppException('Network request failed.', details: error);
    }

    final decoded = response.body.isEmpty ? null : jsonDecode(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }

    final message = decoded is Map<String, dynamic> && decoded['detail'] is String
        ? decoded['detail'] as String
        : 'Server request failed.';

    if (response.statusCode == 401) {
      throw AuthenticationException(message, statusCode: response.statusCode, details: decoded);
    }
    if (response.statusCode == 409) {
      throw ConflictException(message, statusCode: response.statusCode, details: decoded);
    }
    throw AppException(message, statusCode: response.statusCode, details: decoded);
  }

  Future<Map<String, String>> _headers({
    String? tenantSlugOverride,
    String? accessTokenOverride,
  }) async {
    final token = accessTokenOverride ?? await _accessTokenReader();
    final tenantSlug = tenantSlugOverride ?? await _tenantSlugReader();
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      if (tenantSlug != null && tenantSlug.isNotEmpty) 'X-Tenant-Slug': tenantSlug,
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
    };
  }
}
