"""Small JSON API endpoints used by frontend JS (notifications, quick search)."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from database.db import db
from database.models import Notification, Report

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/notifications")
@login_required
def notifications():
    items = Notification.query.filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()).limit(15).all()
    return jsonify([
        {
            "id": n.id,
            "message": n.message,
            "category": n.category,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for n in items
    ])


@api_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    note = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    note.is_read = True
    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/search")
@login_required
def search_reports():
    query_text = request.args.get("q", "").strip()
    if not query_text:
        return jsonify([])

    like = f"%{query_text}%"
    results = Report.query.filter(
        db.or_(Report.title.ilike(like), Report.description.ilike(like), Report.ministry.ilike(like))
    ).limit(10).all()

    return jsonify([
        {
            "id": r.id,
            "title": r.title,
            "ministry": r.ministry,
            "category": r.predicted_category,
            "risk_level": r.risk_level,
            "url": f"/reports/{r.id}/analysis",
        }
        for r in results
    ])
