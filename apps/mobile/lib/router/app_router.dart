import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/ai_review/presentation/ai_review_center_screen.dart';
import '../features/attendance/presentation/attendance_screen.dart';
import '../features/auth/application/auth_controller.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/dashboard/presentation/dashboard_screen.dart';
import '../features/gamification/presentation/gamification_screen.dart';
import '../features/parents/presentation/parent_simple_mode_screen.dart';
import '../features/settings/presentation/settings_screen.dart';
import '../features/students/presentation/student_list_screen.dart';
import '../features/teachers/presentation/teacher_list_screen.dart';
import '../shared/widgets/app_scaffold.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authControllerProvider);
  final signedIn = authState.asData?.value != null;

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final loggingIn = state.uri.path == '/login';
      if (!signedIn && !loggingIn) {
        return '/login';
      }
      if (signedIn && loggingIn) {
        return '/dashboard';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) {
          return AppScaffold(location: state.uri.path, child: child);
        },
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/students',
            builder: (context, state) => const StudentListScreen(),
          ),
          GoRoute(
            path: '/teachers',
            builder: (context, state) => const TeacherListScreen(),
          ),
          GoRoute(
            path: '/attendance',
            builder: (context, state) => const AttendanceScreen(),
          ),
          GoRoute(
            path: '/ai-review',
            builder: (context, state) => const AIReviewCenterScreen(),
          ),
          GoRoute(
            path: '/gamification',
            builder: (context, state) => const GamificationScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/parent-simple',
        builder: (context, state) => const ParentSimpleModeScreen(),
      ),
    ],
  );
});
