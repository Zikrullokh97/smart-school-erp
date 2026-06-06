import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class AppScaffold extends StatelessWidget {
  const AppScaffold({
    required this.location,
    required this.child,
    super.key,
  });

  final String location;
  final Widget child;

  static const _destinations = [
    _NavigationTarget('/dashboard', 'Dashboard', Icons.dashboard_outlined, Icons.dashboard),
    _NavigationTarget('/students', 'Students', Icons.school_outlined, Icons.school),
    _NavigationTarget('/teachers', 'Teachers', Icons.badge_outlined, Icons.badge),
    _NavigationTarget('/attendance', 'Attendance', Icons.fact_check_outlined, Icons.fact_check),
    _NavigationTarget('/settings', 'Settings', Icons.settings_outlined, Icons.settings),
  ];

  @override
  Widget build(BuildContext context) {
    final selectedIndex = _destinations.indexWhere((item) => location.startsWith(item.path));
    final safeIndex = selectedIndex < 0 ? 0 : selectedIndex;
    final wide = MediaQuery.sizeOf(context).width >= 720;

    if (wide) {
      return Scaffold(
        appBar: AppBar(title: Text(_titleFor(location))),
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: safeIndex,
              labelType: NavigationRailLabelType.all,
              onDestinationSelected: (index) => context.go(_destinations[index].path),
              destinations: [
                for (final destination in _destinations)
                  NavigationRailDestination(
                    icon: Icon(destination.icon),
                    selectedIcon: Icon(destination.selectedIcon),
                    label: Text(destination.label),
                  ),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(child: child),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(_titleFor(location))),
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: safeIndex,
        onDestinationSelected: (index) => context.go(_destinations[index].path),
        destinations: [
          for (final destination in _destinations)
            NavigationDestination(
              icon: Icon(destination.icon),
              selectedIcon: Icon(destination.selectedIcon),
              label: destination.label,
            ),
        ],
      ),
    );
  }

  String _titleFor(String location) {
    if (location.startsWith('/students')) return 'Students';
    if (location.startsWith('/teachers')) return 'Teachers';
    if (location.startsWith('/attendance')) return 'Attendance';
    if (location.startsWith('/ai-review')) return 'AI Review';
    if (location.startsWith('/settings')) return 'Settings';
    if (location.startsWith('/parent-simple')) return 'Parent';
    if (location.startsWith('/gamification')) return 'Gamification';
    return 'Dashboard';
  }
}

class _NavigationTarget {
  const _NavigationTarget(this.path, this.label, this.icon, this.selectedIcon);

  final String path;
  final String label;
  final IconData icon;
  final IconData selectedIcon;
}
