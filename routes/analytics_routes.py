"""Interactive analytics dashboards: pie/bar/line charts, heat maps, comparisons."""
import calendar
from datetime import date

from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from sqlalchemy import func

from database.db import db
from database.models import MinistryPerformance, Report

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@login_required
def index():
    return render_template("analytics.html")


@analytics_bp.route("/api/category-distribution")
@login_required
def category_distribution():
    rows = (
        db.session.query(Report.predicted_category, func.count(Report.id))
        .group_by(Report.predicted_category)
        .all()
    )
    return jsonify({"labels": [r[0] or "Unclassified" for r in rows], "values": [r[1] for r in rows]})


@analytics_bp.route("/api/priority-breakdown")
@login_required
def priority_breakdown():
    rows = db.session.query(Report.priority, func.count(Report.id)).group_by(Report.priority).all()
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@analytics_bp.route("/api/monthly-reports")
@login_required
def monthly_reports():
    rows = (
        db.session.query(
            func.strftime("%Y-%m", Report.created_at).label("month"),
            func.count(Report.id),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    return jsonify({"labels": [r[0] for r in rows], "values": [r[1] for r in rows]})


@analytics_bp.route("/api/ministry-comparison")
@login_required
def ministry_comparison():
    rows = (
        db.session.query(
            MinistryPerformance.ministry,
            func.avg(MinistryPerformance.performance_score),
            func.avg(MinistryPerformance.avg_resolution_days),
        )
        .group_by(MinistryPerformance.ministry)
        .all()
    )
    return jsonify({
        "labels": [r[0] for r in rows],
        "performance": [round(r[1], 1) for r in rows],
        "resolution_days": [round(r[2], 1) for r in rows],
    })


@analytics_bp.route("/api/heatmap")
@login_required
def heatmap():
    """Ministry (rows) x month (columns) report volume heat map."""
    rows = (
        db.session.query(
            MinistryPerformance.ministry,
            MinistryPerformance.month,
            MinistryPerformance.year,
            MinistryPerformance.reports_count,
        ).all()
    )

    ministries = sorted({r[0] for r in rows})
    months = sorted({(r[2], r[1]) for r in rows})
    month_labels = [f"{calendar.month_abbr[m]} {y}" for y, m in months]

    matrix = []
    for ministry in ministries:
        row_values = []
        for year, month in months:
            match = next((r[3] for r in rows if r[0] == ministry and r[1] == month and r[2] == year), 0)
            row_values.append(match)
        matrix.append(row_values)

    return jsonify({"ministries": ministries, "months": month_labels, "matrix": matrix})


@analytics_bp.route("/api/risk-levels")
@login_required
def risk_levels():
    rows = db.session.query(Report.risk_level, func.count(Report.id)).group_by(Report.risk_level).all()
    return jsonify({"labels": [r[0] or "Unassessed" for r in rows], "values": [r[1] for r in rows]})
