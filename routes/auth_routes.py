"""Authentication: login, logout, registration."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from database.db import db
from database.models import Role, User
from utils.helpers import log_activity

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active_user:
                flash("Your account has been deactivated. Contact an administrator.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity(user.id, "Login", f"{user.full_name} logged in.")
            flash(f"Welcome back, {user.full_name}.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    roles = Role.query.filter(Role.name != "Administrator").all()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        ministry = request.form.get("ministry", "").strip()
        job_title = request.form.get("job_title", "").strip()
        role_id = request.form.get("role_id")

        errors = []
        if not full_name or not email or not password:
            errors.append("Full name, email and password are required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("auth/register.html", roles=roles)

        role = Role.query.get(role_id) or Role.query.filter_by(name="Viewer").first()
        user = User(full_name=full_name, email=email, ministry=ministry, job_title=job_title, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, "Account Created", f"{user.full_name} registered an account.")

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", roles=roles)


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "Logout", f"{current_user.full_name} logged out.")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
