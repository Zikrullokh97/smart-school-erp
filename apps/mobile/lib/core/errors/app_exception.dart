class AppException implements Exception {
  const AppException(this.message, {this.statusCode, this.details});

  final String message;
  final int? statusCode;
  final Object? details;

  @override
  String toString() => 'AppException($statusCode): $message';
}

class OfflineException extends AppException {
  const OfflineException([super.message = 'Offline operation queued.']);
}

class AuthenticationException extends AppException {
  const AuthenticationException(super.message, {super.statusCode, super.details});
}

class ConflictException extends AppException {
  const ConflictException(super.message, {super.statusCode, super.details});
}
