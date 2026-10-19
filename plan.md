# PhantomVault Pro implementation plan

## Product
A private trading workspace for evidence, journaling, top-down analysis, AI-assisted process review, and performance analytics.

## Design
- **Direction:** terminal-luxe editorial, inspired by institutional trading workstations and archival notebooks.
- **Principles:** dark charcoal surfaces, warm gold signal color, quiet borders, dense but readable information hierarchy.
- **Color philosophy:** gold marks decisions and progress; slate blue-gray supports analysis; red/green are reserved for outcome semantics.
- **Layout paradigm:** fixed rail navigation with a fluid content canvas and card clusters rather than a generic centered dashboard.
- **Signature elements:** gold hairline rules, numbered section labels, compact metric cards, and evidence thumbnails.
- **Interaction:** forms preserve context and show explicit success/error states; missing analysis confirmations remain visible.
- **Typography:** Inter for UI/body, Space Grotesk for display labels.
- **Brand essence:** a calm evidence locker for traders who want to improve process, not chase predictions. Precise, reflective, disciplined.
- **Brand voice:** “Keep the evidence.” / “Outcome is data. Process is the edge.”
- **Wordmark:** PHANTOMVAULT in tracked uppercase with a small gold vault-mark square.
- **Signature color:** #d8ad62.

## Implementation
Flask application factory with Flask-SQLAlchemy models, Flask-Login sessions, Werkzeug password hashing, CSRF tokens, PostgreSQL/SQLite URL normalization, optional Cloudinary image storage, and optional OpenAI-compatible AI coaching. Server-rendered Jinja templates are enhanced with lightweight JavaScript for theme persistence, chart rendering, image preview, and form behavior.

Core modules: authentication, dashboard, trades, screenshot vault, journal, top-down analysis, AI review history, analytics, CSV export.

## Structure
- `app/`: configuration, extensions, models, routes, storage and AI helpers.
- `templates/`: shared shell plus page templates.
- `static/`: responsive CSS and client-side interactions.
- `migrations/`: starter SQL notes; production schema is created by `flask db upgrade` / startup fallback.
- `render.yaml`, `Dockerfile`, `Procfile`: Render deployment options.
- `README.md`: setup, environment variables, deployment and security notes.
