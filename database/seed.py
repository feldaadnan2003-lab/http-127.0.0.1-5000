"""Seeds initial roles, a default admin account and sample demo data on first run."""
import random
from datetime import date, datetime, timedelta

from database.db import db
from database.models import ActivityLog, MinistryPerformance, Report, Role, User

ROLE_DEFINITIONS = [
    {
        "name": "Administrator",
        "description": "Full system access including user management and settings.",
        "permissions": "manage_users,manage_roles,manage_reports,view_analytics,manage_settings,view_logs",
    },
    {
        "name": "Decision Maker",
        "description": "Senior official reviewing AI recommendations and ministry performance.",
        "permissions": "manage_reports,view_analytics",
    },
    {
        "name": "Analyst",
        "description": "Submits and analyzes reports across ministries.",
        "permissions": "manage_reports,view_analytics",
    },
    {
        "name": "Viewer",
        "description": "Read-only access to dashboards and analytics.",
        "permissions": "view_analytics",
    },
]

DEMO_REPORTS = [
    ("Road collapse near central bridge", "A major road collapse was reported in the capital district, blocking traffic for over three hours and damaging nearby utility lines.", "Infrastructure", "High"),
    ("Hospital medicine shortage", "The main hospital in the northern province is reporting a shortage of essential medicines and vaccine supplies.", "Public Health", "Critical"),
    ("Teacher shortage in secondary schools", "Teacher shortages in the eastern governorate have led to increased class sizes and reduced instructional quality.", "Education", "Medium"),
    ("Procurement irregularities flagged", "An internal audit uncovered irregularities in procurement contracts issued by the municipal office.", "Corruption & Compliance", "Critical"),
    ("Rising unemployment after plant closure", "Unemployment figures increased following the closure of a major manufacturing plant in the western district.", "Economy", "High"),
    ("Coastal pollution levels rising", "Air quality monitors recorded pollution levels exceeding national safety standards near the coastal region.", "Environment", "Medium"),
    ("Identification document delays", "Citizens report long wait times when applying for identification documents in the central metropolitan area.", "Public Services", "Low"),
    ("Increase in petty theft", "A rise in petty theft incidents has been recorded across the southern region over the past month.", "Security", "Medium"),
]


def seed_roles():
    if Role.query.count() > 0:
        return
    for definition in ROLE_DEFINITIONS:
        db.session.add(Role(**definition))
    db.session.commit()


def seed_users():
    if User.query.count() > 0:
        return

    admin_role = Role.query.filter_by(name="Administrator").first()
    decision_role = Role.query.filter_by(name="Decision Maker").first()
    analyst_role = Role.query.filter_by(name="Analyst").first()
    viewer_role = Role.query.filter_by(name="Viewer").first()

    demo_users = [
        ("System Administrator", "admin@gov-dss.local", "Admin@12345", "Ministry of Interior", "System Administrator", admin_role),
        ("Sarah Al-Amin", "decision.maker@gov-dss.local", "Decision@123", "Office of the Cabinet", "Senior Decision Maker", decision_role),
        ("Omar Al-Rashid", "analyst@gov-dss.local", "Analyst@123", "Ministry of Health", "Policy Analyst", analyst_role),
        ("Lina Haddad", "viewer@gov-dss.local", "Viewer@123", "Ministry of Education", "Observer", viewer_role),
    ]

    for full_name, email, password, ministry, job_title, role in demo_users:
        user = User(
            full_name=full_name,
            email=email,
            ministry=ministry,
            job_title=job_title,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
    db.session.commit()


def seed_ministry_performance():
    if MinistryPerformance.query.count() > 0:
        return

    ministries = [
        "Ministry of Health", "Ministry of Education", "Ministry of Interior",
        "Ministry of Finance", "Ministry of Transportation", "Ministry of Energy",
        "Ministry of Agriculture", "Ministry of Justice",
    ]
    today = date.today()
    for months_back in range(6):
        month_date = today.replace(day=1) - timedelta(days=months_back * 30)
        for ministry in ministries:
            reports_count = random.randint(15, 90)
            resolved = int(reports_count * random.uniform(0.55, 0.95))
            db.session.add(MinistryPerformance(
                ministry=ministry,
                month=month_date.month,
                year=month_date.year,
                reports_count=reports_count,
                resolved_count=resolved,
                avg_resolution_days=round(random.uniform(1.5, 14.0), 1),
                performance_score=round((resolved / reports_count) * 100, 1),
            ))
    db.session.commit()


def seed_reports():
    if Report.query.count() > 0:
        return

    from ai_engine.classifier import get_classifier
    from ai_engine.recommendation_engine import analyze_report
    from ai_engine.text_processor import extract_keywords
    from flask import current_app

    analyst = User.query.filter_by(email="analyst@gov-dss.local").first()
    classifier = None
    try:
        classifier = get_classifier(current_app.config["AI_MODEL_DIR"])
    except Exception:
        classifier = None

    ministries = current_app.config["MINISTRIES"]

    for idx, (title, description, expected_category, priority) in enumerate(DEMO_REPORTS):
        category = expected_category
        confidence = 0.82
        keywords = []

        if classifier and classifier.is_ready():
            result = classifier.predict(description)
            category = result["category"]
            confidence = result["confidence"]
            keywords = extract_keywords(description, classifier.vectorizer)

        analysis = analyze_report(title, description, priority, category, confidence, keywords)

        report = Report(
            title=title,
            description=description,
            ministry=ministries[idx % len(ministries)],
            department="General Directorate",
            priority=priority,
            report_date=date.today() - timedelta(days=idx * 3),
            status=random.choice(["Pending Review", "Under Investigation", "Resolved"]),
            predicted_category=category,
            confidence_score=confidence,
            keywords=", ".join(keywords),
            risk_level=analysis["risk_level"],
            recommendation=analysis["recommendation"],
            suggested_action=analysis["suggested_action"],
            decision_priority=analysis["decision_priority"],
            summary=analysis["summary"],
            submitted_by_id=analyst.id if analyst else None,
            created_at=datetime.utcnow() - timedelta(days=idx * 3),
        )
        db.session.add(report)
    db.session.commit()


def seed_activity_log():
    if ActivityLog.query.count() > 0:
        return
    admin = User.query.filter_by(email="admin@gov-dss.local").first()
    if not admin:
        return
    db.session.add(ActivityLog(
        user_id=admin.id,
        action="System Initialized",
        description="Government Decision Support Agent deployed and seeded with demo data.",
        ip_address="127.0.0.1",
    ))
    db.session.commit()


def seed_all():
    seed_roles()
    seed_users()
    seed_ministry_performance()
    seed_reports()
    seed_activity_log()
