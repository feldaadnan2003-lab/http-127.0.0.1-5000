"""Main authenticated dashboard: statistics, charts, recent reports, alerts."""
from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from database.db import db
from database.models import MinistryPerformance, Notification, Report

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    total_reports = Report.query.count()
    pending_reports = Report.query.filter_by(status="Pending Review").count()
    resolved_reports = Report.query.filter_by(status="Resolved").count()
    critical_reports = Report.query.filter(Report.risk_level == "Critical").count()

    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(6).all()

    category_counts = (
        db.session.query(Report.predicted_category, func.count(Report.id))
        .group_by(Report.predicted_category)
        .all()
    )
    priority_counts = (
        db.session.query(Report.priority, func.count(Report.id))
        .group_by(Report.priority)
        .all()
    )

    thirty_days_ago = date.today() - timedelta(days=30)
    trend_rows = (
        db.session.query(Report.created_at, Report.id)
        .filter(Report.created_at >= thirty_days_ago)
        .all()
    )
    trend_buckets = {}
    for created_at, _ in trend_rows:
        key = created_at.strftime("%Y-%m-%d")
        trend_buckets[key] = trend_buckets.get(key, 0) + 1

    ministry_perf = (
        db.session.query(
            MinistryPerformance.ministry,
            func.avg(MinistryPerformance.performance_score).label("avg_score"),
        )
        .group_by(MinistryPerformance.ministry)
        .order_by(func.avg(MinistryPerformance.performance_score).desc())
        .limit(6)
        .all()
    )

    alerts = Report.query.filter(Report.risk_level.in_(["Critical", "High"])) \
        .order_by(Report.created_at.desc()).limit(5).all()

    notifications = Notification.query.filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()).limit(8).all()

    return render_template(
        "dashboard.html",
        total_reports=total_reports,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports,
        critical_reports=critical_reports,
        recent_reports=recent_reports,
        category_counts=category_counts,
        priority_counts=priority_counts,
        trend_buckets=trend_buckets,
        ministry_perf=ministry_perf,
        alerts=alerts,
        notifications=notifications,
    )
