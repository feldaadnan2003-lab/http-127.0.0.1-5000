"""Access-control decorators built on top of Flask-Login."""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*role_names):
    """Restrict a view to users whose role name is in ``role_names``."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role_name not in role_names:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("dashboard.index"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def permission_required(permission_key):
    """Restrict a view to users whose role grants a specific permission key."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if not current_user.role or not current_user.role.has_permission(permission_key):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
