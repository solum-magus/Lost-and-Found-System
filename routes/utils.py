from functools import wraps

from flask import abort, flash, redirect, session, url_for


def home_for(role):
    """Where each role lands after logging in."""
    return "admin.dashboard" if role == "Admin" else "user.dashboard"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "Admin":
            abort(403)
        return view(*args, **kwargs)
    return login_required(wrapped)
