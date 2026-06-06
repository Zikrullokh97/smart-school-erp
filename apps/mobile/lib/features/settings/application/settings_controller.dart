import 'package:flutter_riverpod/flutter_riverpod.dart';

class ThemeSettings {
  const ThemeSettings({
    this.highContrast = false,
    this.largeText = false,
    this.largeButtons = false,
    this.simpleMode = false,
    this.backgroundSync = true,
  });

  final bool highContrast;
  final bool largeText;
  final bool largeButtons;
  final bool simpleMode;
  final bool backgroundSync;

  ThemeSettings copyWith({
    bool? highContrast,
    bool? largeText,
    bool? largeButtons,
    bool? simpleMode,
    bool? backgroundSync,
  }) {
    return ThemeSettings(
      highContrast: highContrast ?? this.highContrast,
      largeText: largeText ?? this.largeText,
      largeButtons: largeButtons ?? this.largeButtons,
      simpleMode: simpleMode ?? this.simpleMode,
      backgroundSync: backgroundSync ?? this.backgroundSync,
    );
  }
}

class SettingsController extends StateNotifier<ThemeSettings> {
  SettingsController() : super(const ThemeSettings());

  void setHighContrast(bool value) => state = state.copyWith(highContrast: value);

  void setLargeText(bool value) => state = state.copyWith(largeText: value);

  void setLargeButtons(bool value) => state = state.copyWith(largeButtons: value);

  void setSimpleMode(bool value) => state = state.copyWith(simpleMode: value);

  void setBackgroundSync(bool value) => state = state.copyWith(backgroundSync: value);
}

final settingsControllerProvider =
    StateNotifierProvider<SettingsController, ThemeSettings>((ref) => SettingsController());
