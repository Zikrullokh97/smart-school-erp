import 'package:flutter/material.dart';

import '../../features/settings/application/settings_controller.dart';

class AppTheme {
  static ThemeData light(ThemeSettings settings) {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF0F766E),
        primary: const Color(0xFF0F766E),
        secondary: const Color(0xFFB45309),
        tertiary: const Color(0xFF334155),
      ),
    );
    return _applyScale(base, settings);
  }

  static ThemeData dark(ThemeSettings settings) {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF14B8A6),
        brightness: Brightness.dark,
        primary: const Color(0xFF5EEAD4),
        secondary: const Color(0xFFFBBF24),
        tertiary: const Color(0xFFCBD5E1),
      ),
    );
    return _applyScale(base, settings);
  }

  static ThemeData highContrast(ThemeSettings settings) {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: const ColorScheme.highContrastDark(
        primary: Color(0xFFFFFF00),
        secondary: Color(0xFF00E5FF),
        surface: Colors.black,
        onSurface: Colors.white,
      ),
    );
    return _applyScale(base, settings);
  }

  static ThemeData _applyScale(ThemeData theme, ThemeSettings settings) {
    final scale = settings.largeText ? 1.18 : 1.0;
    return theme.copyWith(
      textTheme: theme.textTheme.apply(fontSizeFactor: scale),
      visualDensity: settings.largeButtons ? VisualDensity.comfortable : VisualDensity.standard,
      navigationBarTheme: NavigationBarThemeData(
        labelTextStyle: WidgetStatePropertyAll(theme.textTheme.labelMedium),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: Size.fromHeight(settings.largeButtons ? 56 : 48),
        ),
      ),
    );
  }
}
