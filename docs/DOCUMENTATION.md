# Architecture Documentation

## Overview

The Government Decision Support Agent is a server-rendered Flask application (Jinja2 templates + vanilla JS, no separate SPA build step). It combines a traditional CRUD web app (reports, users, roles) with an embedded NLP pipeline that runs synchronously on report submission.

## Request flow: report submission → AI analysis

1. `routes/report_routes.py: new_report()` validates the form, saves uploads via `utils/helpers.save_upload`, and persists a `Report` row.
2. `run_ai_analysis(report)` builds `f"{title}. {description}"` and:
   - Loads the singleton classifier via `ai_engine.classifier.get_classifier()` (lazy-loaded once per process from `ai_engine/saved_models/`).
   - `ReportClassifier.predict()` runs the same `preprocess()` pipeline used in training (clean → tokenize → lemmatize), vectorizes with the fitted TF-IDF vectorizer, and returns the predicted category + confidence + top-3 alternatives.
   - `ai_engine.text_processor.extract_keywords()` ranks tokens by TF-IDF weight (from the trained vectorizer's IDF table) to surface the report's most distinctive terms.
   - `ai_engine.recommendation_engine.analyze_report()` combines the predicted category, the analyst-assigned priority, model confidence, and keyword risk-term matching into a risk level, decision priority, recommendation, and suggested action.
3. Results are written back onto the `Report` row and the user is redirected to `/reports/<id>/analysis`.

## AI/NLP pipeline details

- **Cleaning** (`text_processor.clean_text`): lowercase, strip URLs/digits/punctuation.
- **Tokenization** (`text_processor.tokenize`): NLTK `word_tokenize` + `WordNetLemmatizer`, with an extended stopword list (English stopwords + domain filler words like "report", "ministry").
- **Vectorization**: `TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True)`.
- **Classification**: `LogisticRegression(C=5.0, class_weight="balanced")`, trained with an 80/20 stratified split.
- **Training data**: `data/generate_dataset.py` produces 800 labeled samples (8 categories × 10 templates × 10 region variants) — synthetic but linguistically realistic government-report sentences. Regenerate with `python data/generate_dataset.py`, retrain with `python ai_engine/train_model.py`.
- **Recommendation heuristics** (not ML): `recommendation_engine.py` maps category → suggested action, and combines priority + confidence + keyword risk-term hits (e.g. "collapse", "outbreak", "corruption") into a 4-level risk score (Low/Medium/High/Critical).

## Access control

- `Role` rows store a comma-separated `permissions` string (e.g. `manage_users,manage_reports`).
- `utils/decorators.role_required(*names)` restricts a view by role name; `permission_required(key)` restricts by permission key. Only `role_required` is currently used (all admin routes require the "Administrator" role) — `permission_required` is available for finer-grained checks if roles are split further.

## Data model summary (`database/models.py`)

- `User` — auth + profile, linked to a `Role`.
- `Role` — name + permissions string.
- `Report` — submission fields + AI analysis output fields (category, confidence, keywords, risk_level, recommendation, suggested_action, decision_priority, summary).
- `MinistryPerformance` — monthly aggregate (reports_count, resolved_count, avg_resolution_days, performance_score) used by the analytics/heatmap endpoints.
- `ActivityLog` — audit trail, written by `utils/helpers.log_activity` on login/logout/report/user/role actions.
- `Notification` — per-user in-app notifications, polled by `static/js/main.js` via `/api/notifications`.

## Frontend architecture

- `templates/base.html` is the root shell (loader, toasts, CSS/JS includes).
- `templates/layout_public.html` (navbar + footer) and `templates/layout_app.html` (sidebar + topbar) both extend `base.html`; every page extends one of the two.
- CSS is split into `main.css` (marketing site + shared components), `dashboard.css` (app shell, panels, tables), `animations.css` (keyframes + scroll-reveal), `dark-mode.css` (`[data-theme="dark"]` variable overrides).
- Theme preference persists via `localStorage` (`static/js/theme-toggle.js`).
- Charts use Chart.js from CDN; every canvas is wrapped in a `.chart-box` container with a fixed CSS height — omitting this causes an infinite-growth feedback loop with `maintainAspectRatio: false`.

## Extending the system

- **New report category**: add it to `Config.REPORT_CATEGORIES`, add matching templates to `data/generate_dataset.py`, regenerate the dataset, retrain.
- **New role/permission**: add the permission key to `routes/admin_routes.py: ALL_PERMISSIONS`, and gate routes with `@permission_required("your_key")`.
- **New chart on Analytics**: add a JSON endpoint to `routes/analytics_routes.py`, a canvas + `.chart-box` wrapper to `templates/analytics.html`, and a loader function in `static/js/analytics.js`.
