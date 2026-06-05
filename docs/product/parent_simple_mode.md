# Parent Simple Mode UI Specification

Purpose
- Provide a low-visual-complexity, high-accessibility parent interface focused on essential actions: attendance notifications, message inbox, student progress summary, quick replies, and emergency contact.

Design Principles
- Minimal visual clutter: single-column layout, large touch targets, high-contrast colors, simplified language (Kyrgyz/Russian/English localization), and large fonts by default.
- Accessibility first: screen-reader friendly semantics, clear focus states, keyboard navigation, and ARIA labels where appropriate.
- Performance and offline resilience: small payloads, lazy-load assets, local cache of recent messages and notifications.
- Progressive enhancement: simple mode toggle in parent profile (`ui_preferences.simple_mode=true`) falls back gracefully to full UI when features are unavailable.

Core Screens
- Home / Dashboard
  - Student cards (one per child) with: name, current attendance status, today's summary, quick action to message teacher.
  - Notifications list (unread first) with concise messages and time.
- Messages
  - Inbox listing threads; simple compose with pre-defined quick replies and optional free text.
- Progress
  - Compact grade/attendance summary per subject with visual badges for positive milestones.
- Settings
  - Toggle: Simple Mode (on/off)
  - Accessibility: Font size (small/medium/large), High contrast, Text-only mode (disable icons)
  - Notifications: toggle for SMS, push, in-app

Interaction Patterns
- One-tap primary actions: open message, acknowledge notification, mark as seen.
- Quick Replies: configurable set in `ui_preferences.simple_mode_quick_replies` (up to 6 phrases).
- Offline: allow composing messages offline; queue operations to offline sync mechanism with a `source=parent_simple_mode` flag.

Data Contracts
- Parent profile includes `ui_preferences` JSON with keys:
  - `simple_mode`: boolean
  - `font_size`: enum `small|medium|large`
  - `high_contrast`: boolean
  - `quick_replies`: list[str]
  - `text_only`: boolean

Security & Privacy
- Ensure parent tokens are scoped to parent records and limited to reading their children's data.
- Any images or attachments are disabled by default in simple mode to reduce bandwidth and privacy exposure.

Implementation Notes
- Frontend: single minimal React/Next.js route with server-side rendering for first load; small client bundle for simple mode.
- Backend: `parents` CRUD already supports `ui_preferences` JSONB; ensure validation on update for allowed keys.
- Tests: end-to-end tests for toggle behavior, `ui_preferences` persistence, offline queued messages submission.

Localization
- Provide Kyrgyz, Russian, and English translations for all labels. Keep messages short and use plain language.

Metrics
- Track adoption percentage of simple mode, average session length, and error/failure rate for queued offline messages.
