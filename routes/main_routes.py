"""Public marketing site: home page with hero, features, services, FAQ, contact, etc."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    stats = {
        "ministries": len(current_app.config["MINISTRIES"]),
        "reports_processed": 12480,
        "accuracy_rate": 94.6,
        "avg_response_hours": 6,
    }
    return render_template("home.html", stats=stats)


@main_bp.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill in all fields before submitting.", "danger")
    else:
        # In production this would enqueue an email / ticket. Kept lightweight here.
        flash("Thank you for reaching out. Our team will respond shortly.", "success")

    return redirect(url_for("main.home") + "#contact")
