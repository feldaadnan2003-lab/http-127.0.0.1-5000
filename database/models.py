"""SQLAlchemy ORM models for the Government Decision Support Agent."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text, default="")  # comma separated permission keys

    users = db.relationship("User", back_populates="role")

    def permission_list(self):
        return [p.strip() for p in self.permissions.split(",") if p.strip()]

    def has_permission(self, key):
        return key in self.permission_list()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    ministry = db.Column(db.String(120))
    job_title = db.Column(db.String(120))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    role = db.relationship("Role", back_populates="users")
    reports = db.relationship("Report", back_populates="submitted_by", lazy="dynamic")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_active(self):
        return self.is_active_user

    @property
    def role_name(self):
        return self.role.name if self.role else "Unassigned"


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ministry = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    report_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(30), default="Pending Review")

    file_path = db.Column(db.String(300))
    image_path = db.Column(db.String(300))

    # AI analysis results
    predicted_category = db.Column(db.String(80))
    confidence_score = db.Column(db.Float)
    keywords = db.Column(db.Text)  # comma separated
    risk_level = db.Column(db.String(20))
    recommendation = db.Column(db.Text)
    suggested_action = db.Column(db.Text)
    decision_priority = db.Column(db.String(20))
    summary = db.Column(db.Text)

    submitted_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitted_by = db.relationship("User", back_populates="reports")

    def keyword_list(self):
        return [k.strip() for k in (self.keywords or "").split(",") if k.strip()]


class MinistryPerformance(db.Model):
    __tablename__ = "ministry_performance"

    id = db.Column(db.Integer, primary_key=True)
    ministry = db.Column(db.String(120), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    reports_count = db.Column(db.Integer, default=0)
    resolved_count = db.Column(db.Integer, default=0)
    avg_resolution_days = db.Column(db.Float, default=0.0)
    performance_score = db.Column(db.Float, default=0.0)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    message = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(20), default="info")  # info, warning, success, danger
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
