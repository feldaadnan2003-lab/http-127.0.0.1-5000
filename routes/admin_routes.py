"""Administration panel: user management, roles/permissions, reports, settings, activity logs."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.db import db
from database.models import ActivityLog, Report, Role, User
from utils.decorators import role_required
from utils.helpers import log_activity

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALL_PERMISSIONS = [
    ("manage_users", "Manage Users"),
    ("manage_roles", "Manage Roles & Permissions"),
    ("manage_reports", "Manage Reports"),
    ("view_analytics", "View Analytics"),
    ("manage_settings", "Manage System Settings"),
    ("view_logs", "View Activity Logs"),
]


@admin_bp.route("/")
@login_required
@role_required("Administrator")
def index():
    return redirect(url_for("admin.users"))


@admin_bp.route("/users")
@login_required
@role_required("Administrator")
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    roles = Role.query.all()
    return render_template("admin/users.html", users=all_users, roles=roles)


@admin_bp.route("/users/<int:user_id>/update", methods=["POST"])
@login_required
@role_required("Administrator")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    role_id = request.form.get("role_id")
    is_active = request.form.get("is_active") == "on"

    if role_id:
        user.role_id = int(role_id)
    user.is_active_user = is_active
    db.session.commit()

    log_activity(current_user.id, "User Updated", f"Updated user {user.email}.")
    flash(f"User {user.full_name} updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("Administrator")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))

    log_activity(current_user.id, "User Deleted", f"Deleted user {user.email}.")
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/roles")
@login_required
@role_required("Administrator")
def roles():
    all_roles = Role.query.all()
    return render_template("admin/roles.html", roles=all_roles, all_permissions=ALL_PERMISSIONS)


@admin_bp.route("/roles/<int:role_id>/update", methods=["POST"])
@login_required
@role_required("Administrator")
def update_role(role_id):
    role = Role.query.get_or_404(role_id)
    selected = request.form.getlist("permissions")
    role.permissions = ",".join(selected)
    db.session.commit()
    log_activity(current_user.id, "Role Updated", f"Updated permissions for role {role.name}.")
    flash(f"Permissions updated for {role.name}.", "success")
    return redirect(url_for("admin.roles"))


@admin_bp.route("/reports")
@login_required
@role_required("Administrator")
def reports():
    all_reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin/reports.html", reports=all_reports)


@admin_bp.route("/reports/<int:report_id>/delete", methods=["POST"])
@login_required
@role_required("Administrator")
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    log_activity(current_user.id, "Report Deleted", f"Deleted report '{report.title}'.")
    db.session.delete(report)
    db.session.commit()
    flash("Report deleted.", "success")
    return redirect(url_for("admin.reports"))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("Administrator")
def settings():
    if request.method == "POST":
        log_activity(current_user.id, "Settings Updated", "System settings were modified.")
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))

    return render_template(
        "admin/settings.html",
        ministries=current_app.config["MINISTRIES"],
        categories=current_app.config["REPORT_CATEGORIES"],
    )


@admin_bp.route("/logs")
@login_required
@role_required("Administrator")
def logs():
    activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(200).all()
    return render_template("admin/activity_logs.html", logs=activity)
