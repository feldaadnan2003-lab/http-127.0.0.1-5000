"""Small shared helpers: file validation/saving, activity logging, notifications."""
import os
import uuid
from datetime import datetime

from flask import current_app, request
from werkzeug.utils import secure_filename

from database.db import db
from database.models import ActivityLog, Notification


def allowed_document(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"]


def allowed_image(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_upload(file_storage, subfolder="documents"):
    """Save an uploaded werkzeug FileStorage to UPLOAD_FOLDER/subfolder with a unique name."""
    if not file_storage or file_storage.filename == "":
        return None

    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, unique_name)
    file_storage.save(full_path)
    return os.path.join(subfolder, unique_name).replace("\\", "/")


def log_activity(user_id, action, description=""):
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=request.remote_addr if request else None,
        created_at=datetime.utcnow(),
    )
    db.session.add(entry)
    db.session.commit()


def notify(user_id, message, category="info"):
    note = Notification(user_id=user_id, message=message, category=category)
    db.session.add(note)
    db.session.commit()
    return note
