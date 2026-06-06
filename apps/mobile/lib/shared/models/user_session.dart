class UserSession {
  const UserSession({
    required this.tenantSlug,
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    required this.user,
  });

  final String tenantSlug;
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final CurrentUser user;
}

class CurrentUser {
  const CurrentUser({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.status,
    required this.locale,
    required this.roleCodes,
  });

  factory CurrentUser.fromJson(Map<String, dynamic> json) {
    return CurrentUser(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      status: json['status'] as String,
      locale: json['locale'] as String,
      roleCodes: (json['role_codes'] as List<dynamic>? ?? const [])
          .cast<String>()
          .toList(growable: false),
    );
  }

  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String status;
  final String locale;
  final List<String> roleCodes;

  String get displayName => '$firstName $lastName';
}
