typedef VoiceActionHandler = Future<void> Function();

class VoiceAssistantAction {
  const VoiceAssistantAction({
    required this.intent,
    required this.phrases,
    required this.handler,
  });

  final String intent;
  final List<String> phrases;
  final VoiceActionHandler handler;
}

class VoiceAssistantRegistry {
  final Map<String, VoiceAssistantAction> _actions = {};

  void register(VoiceAssistantAction action) {
    _actions[action.intent] = action;
  }

  Future<bool> handlePhrase(String phrase) async {
    final normalized = phrase.trim().toLowerCase();
    for (final action in _actions.values) {
      if (action.phrases.any((candidate) => candidate.toLowerCase() == normalized)) {
        await action.handler();
        return true;
      }
    }
    return false;
  }

  List<VoiceAssistantAction> get actions => List.unmodifiable(_actions.values);
}
