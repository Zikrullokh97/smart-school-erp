class Teacher {
  const Teacher({
    required this.id,
    required this.schoolId,
    required this.employeeNumber,
    required this.firstName,
    required this.lastName,
    required this.hireDate,
    required this.status,
    required this.profile,
    this.userId,
  });

  factory Teacher.fromJson(Map<String, dynamic> json) {
    return Teacher(
      id: json['id'] as String,
      schoolId: json['school_id'] as String,
      userId: json['user_id'] as String?,
      employeeNumber: json['employee_number'] as String,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      hireDate: DateTime.parse(json['hire_date'] as String),
      status: json['status'] as String,
      profile: (json['profile'] as Map<String, dynamic>? ?? const {}),
    );
  }

  final String id;
  final String schoolId;
  final String? userId;
  final String employeeNumber;
  final String firstName;
  final String lastName;
  final DateTime hireDate;
  final String status;
  final Map<String, dynamic> profile;

  String get displayName => '$firstName $lastName';
}
