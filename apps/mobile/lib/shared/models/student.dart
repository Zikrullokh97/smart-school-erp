class Student {
  const Student({
    required this.id,
    required this.schoolId,
    required this.studentNumber,
    required this.firstName,
    required this.lastName,
    required this.dateOfBirth,
    required this.gender,
    required this.status,
    required this.enrollmentDate,
    required this.profile,
    this.middleName,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] as String,
      schoolId: json['school_id'] as String,
      studentNumber: json['student_number'] as String,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      middleName: json['middle_name'] as String?,
      dateOfBirth: DateTime.parse(json['date_of_birth'] as String),
      gender: json['gender'] as String,
      status: json['status'] as String,
      enrollmentDate: DateTime.parse(json['enrollment_date'] as String),
      profile: (json['profile'] as Map<String, dynamic>? ?? const {}),
    );
  }

  final String id;
  final String schoolId;
  final String studentNumber;
  final String firstName;
  final String lastName;
  final String? middleName;
  final DateTime dateOfBirth;
  final String gender;
  final String status;
  final DateTime enrollmentDate;
  final Map<String, dynamic> profile;

  String get displayName {
    final middle = middleName == null || middleName!.isEmpty ? '' : ' ${middleName!}';
    return '$firstName$middle $lastName';
  }
}
