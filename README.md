# Government Decision Support Agent

An AI-powered decision support platform for government ministries. Analysts submit reports, and an NLP pipeline (TF-IDF + Logistic Regression) automatically classifies the issue, extracts keywords, scores risk, and generates an actionable recommendation for decision-makers.

## Features

- **Public site** — hero, features, services, how-it-works, AI capabilities, FAQ, contact.
- **Dashboard** — statistics, category/priority charts, recent reports, alerts, ministry performance, quick actions.
- **Report submission** — ministry/department/priority form with document + image upload.
- **AI analysis** — summary, classification, confidence score, keyword extraction, risk level, recommendation, suggested action, decision priority.
- **Analytics** — pie/bar/line charts, ministry comparison, and a report-volume heat map.
- **Administration** — user management, roles & permissions, report management, settings, activity logs.
- **Light/dark mode**, responsive layout, toast notifications, live in-app notifications, global search.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, SQLite
- **AI/NLP**: Pandas, scikit-learn (TF-IDF + Logistic Regression), NLTK
- **Frontend**: Jinja2 templates, vanilla JS, Chart.js, Font Awesome

## Project Structure

```
├── app.py                   # Flask application factory
├── run.py                   # Entrypoint (python run.py)
├── config.py                # Configuration (ministries, categories, upload rules)
├── requirements.txt
├── ai_engine/
│   ├── text_processor.py    # Cleaning, tokenization, keyword extraction
│   ├── classifier.py        # TF-IDF + Logistic Regression wrapper
│   ├── recommendation_engine.py  # Risk/recommendation heuristics
│   ├── train_model.py       # Trains and persists the model
│   └── saved_models/        # Persisted vectorizer + model (generated)
├── data/
│   ├── generate_dataset.py  # Builds the synthetic labeled dataset
│   └── dataset.csv          # Generated training data (800 samples, 8 categories)
├── database/
│   ├── db.py                # SQLAlchemy instance
│   ├── models.py             # User, Role, Report, MinistryPerformance, ActivityLog, Notification
│   └── seed.py                # First-run demo data seeding
├── routes/                   # Flask blueprints (auth, main, dashboard, report, analytics, admin, api)
├── templates/                 # Jinja2 templates
├── static/{css,js,images}     # Styling, client-side behavior, logo
├── uploads/{documents,images}  # User-uploaded files
└── utils/                     # Decorators (RBAC) and helpers (uploads, logging, notifications)
```

## Getting Started

```bash
pip install -r requirements.txt
python ai_engine/train_model.py   # trains the classifier (run once, or after editing the dataset)
python run.py                     # starts the app on http://localhost:5000
```

The database, upload folders and demo data (roles, users, sample reports, ministry performance) are created automatically on first run.

### Demo accounts

| Role | Email | Password |
|---|---|---|
| Administrator | admin@gov-dss.local | Admin@12345 |
| Decision Maker | decision.maker@gov-dss.local | Decision@123 |
| Analyst | analyst@gov-dss.local | Analyst@123 |
| Viewer | viewer@gov-dss.local | Viewer@123 |

## Retraining the AI model

The classifier is trained on `data/dataset.csv`, a synthetic-but-realistic set of labeled government reports across 8 categories (Infrastructure, Public Health, Education, Security, Economy, Environment, Corruption & Compliance, Public Services). To regenerate the dataset or retrain:

```bash
python data/generate_dataset.py   # optional: regenerate the dataset
python ai_engine/train_model.py   # retrain and persist the model
```

## Notes

- This is a development configuration (SQLite, Flask dev server). For production, set `FLASK_ENV=production`, use a proper WSGI server (gunicorn/waitress), and move secrets into environment variables.
