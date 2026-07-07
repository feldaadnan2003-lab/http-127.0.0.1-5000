"""Report submission workflow and the AI analysis results page."""
from datetime import datetime

from flask import (Blueprint, abort, current_app, flash, redirect,
                    render_template, request, url_for)
from flask_login import current_user, login_required

from ai_engine.classifier import get_classifier
from ai_engine.recommendation_engine import analyze_report
from ai_engine.text_processor import extract_keywords
from database.db import db
from database.models import Report
from utils.helpers import allowed_document, allowed_image, log_activity, notify, save_upload

report_bp = Blueprint("report", __name__, url_prefix="/reports")


@report_bp.route("/")
@login_required
def report_list():
    query = Report.query

    status = request.args.get("status")
    priority = request.args.get("priority")
    ministry = request.args.get("ministry")
    search = request.args.get("q")

    if status:
        query = query.filter(Report.status == status)
    if priority:
        query = query.filter(Report.priority == priority)
    if ministry:
        query = query.filter(Report.ministry == ministry)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Report.title.ilike(like), Report.description.ilike(like)))

    reports = query.order_by(Report.created_at.desc()).all()
    return render_template(
        "reports_list.html",
        reports=reports,
        ministries=current_app.config["MINISTRIES"],
        priorities=current_app.config["PRIORITY_LEVELS"],
    )


@report_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_report():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        ministry = request.form.get("ministry", "").strip()
        department = request.form.get("department", "").strip()
        priority = request.form.get("priority", "Medium")
        report_date_raw = request.form.get("report_date")

        errors = []
        if not title or not description or not ministry or not department:
            errors.append("Title, description, ministry and department are required.")

        document_file = request.files.get("document")
        image_file = request.files.get("image")

        if document_file and document_file.filename and not allowed_document(document_file.filename):
            errors.append("Unsupported document file type.")
        if image_file and image_file.filename and not allowed_image(image_file.filename):
            errors.append("Unsupported image file type.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "report_form.html",
                ministries=current_app.config["MINISTRIES"],
                priorities=current_app.config["PRIORITY_LEVELS"],
                form_data=request.form,
            )

        try:
            report_date = datetime.strptime(report_date_raw, "%Y-%m-%d").date() if report_date_raw else datetime.utcnow().date()
        except ValueError:
            report_date = datetime.utcnow().date()

        document_path = save_upload(document_file, "documents") if document_file else None
        image_path = save_upload(image_file, "images") if image_file else None

        report = Report(
            title=title,
            description=description,
            ministry=ministry,
            department=department,
            priority=priority,
            report_date=report_date,
            file_path=document_path,
            image_path=image_path,
            submitted_by_id=current_user.id,
        )
        db.session.add(report)
        db.session.commit()

        run_ai_analysis(report)

        log_activity(current_user.id, "Report Submitted", f"Submitted report '{title}'.")
        notify(current_user.id, f"AI analysis complete for report '{title}'.", "success")

        flash("Report submitted and analyzed successfully.", "success")
        return redirect(url_for("report.ai_analysis", report_id=report.id))

    return render_template(
        "report_form.html",
        ministries=current_app.config["MINISTRIES"],
        priorities=current_app.config["PRIORITY_LEVELS"],
        form_data={},
    )


def run_ai_analysis(report: Report):
    """Runs the NLP classifier + recommendation engine against a report and persists results."""
    text = f"{report.title}. {report.description}"

    try:
        classifier = get_classifier(current_app.config["AI_MODEL_DIR"])
        prediction = classifier.predict(text)
        keywords = extract_keywords(text, classifier.vectorizer)
    except Exception:
        prediction = {"category": "Public Services", "confidence": 0.5, "top_predictions": []}
        keywords = extract_keywords(text)

    analysis = analyze_report(
        report.title, report.description, report.priority,
        prediction["category"], prediction["confidence"], keywords,
    )

    report.predicted_category = prediction["category"]
    report.confidence_score = prediction["confidence"]
    report.keywords = ", ".join(keywords)
    report.risk_level = analysis["risk_level"]
    report.recommendation = analysis["recommendation"]
    report.suggested_action = analysis["suggested_action"]
    report.decision_priority = analysis["decision_priority"]
    report.summary = analysis["summary"]
    report.updated_at = datetime.utcnow()
    db.session.commit()
    return prediction


@report_bp.route("/<int:report_id>/analysis")
@login_required
def ai_analysis(report_id):
    report = Report.query.get_or_404(report_id)

    classifier = None
    try:
        classifier = get_classifier(current_app.config["AI_MODEL_DIR"])
    except Exception:
        classifier = None

    top_predictions = []
    if classifier and classifier.is_ready():
        top_predictions = classifier.predict(f"{report.title}. {report.description}")["top_predictions"]

    return render_template("ai_analysis.html", report=report, top_predictions=top_predictions)


@report_bp.route("/<int:report_id>")
@login_required
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template("ai_analysis.html", report=report, top_predictions=[])


@report_bp.route("/<int:report_id>/status", methods=["POST"])
@login_required
def update_status(report_id):
    report = Report.query.get_or_404(report_id)
    new_status = request.form.get("status")
    if new_status in ["Pending Review", "Under Investigation", "Resolved", "Escalated"]:
        report.status = new_status
        db.session.commit()
        log_activity(current_user.id, "Status Updated", f"Report #{report.id} set to {new_status}.")
        flash("Report status updated.", "success")
    return redirect(url_for("report.ai_analysis", report_id=report.id))
