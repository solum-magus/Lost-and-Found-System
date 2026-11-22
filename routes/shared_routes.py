from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from models import item_model, user_model
from routes.auth_routes import (EMAIL_RE, NAME_MAX, NAME_MIN, PASSWORD_MAX,
                                PASSWORD_MIN, valid_name)
from routes.utils import login_required

bp = Blueprint("shared", __name__)


@bp.route("/history")
@login_required
def history():
    type_filter = request.args.get("type", "")          
    return render_template("history.html", reports=item_model.all_reports(type_filter),
                           type_filter=type_filter)


@bp.route("/settings")
@login_required
def settings():
    user = user_model.get_by_id(session["user_id"])
    return render_template("settings.html", user=user, errors={}, form={})


@bp.route("/settings/profile", methods=["POST"])
@login_required
def update_profile():
    user = user_model.get_by_id(session["user_id"])
    full_name = " ".join(request.form.get("full_name", "").split())
    email = request.form.get("email", "").strip().lower()
    errors = {}

    if not full_name:
        errors["full_name"] = "Full name is required."
    elif not NAME_MIN <= len(full_name) <= NAME_MAX:
        errors["full_name"] = f"Full name must be {NAME_MIN} to {NAME_MAX} characters."
    elif not valid_name(full_name):
        errors["full_name"] = "Use letters, spaces, periods, hyphens and apostrophes only."

    if not email:
        errors["email"] = "Email is required."
    elif len(email) > 100 or not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    elif user_model.email_taken_by_other(email, user["id"]):
        errors["email"] = "That email is already registered."

    if errors:
        return render_template("settings.html", user=user, errors=errors, form=request.form)

    user_model.update_profile(user["id"], full_name, email)
    session["full_name"] = full_name          # so the sidebar shows the new name
    flash("Profile updated.", "success")
    return redirect(url_for("shared.settings"))


@bp.route("/settings/password", methods=["POST"])
@login_required
def update_password():
    user = user_model.get_by_id(session["user_id"])
    current = request.form.get("current", "")
    new = request.form.get("new", "")
    confirm = request.form.get("confirm", "")
    errors = {}

    if not check_password_hash(user["password"], current):
        errors["current"] = "Current password is incorrect."

    if not new:
        errors["new"] = "New password is required."
    elif len(new) < PASSWORD_MIN:
        errors["new"] = f"Password must be at least {PASSWORD_MIN} characters."
    elif len(new) > PASSWORD_MAX:
        errors["new"] = f"Password must be at most {PASSWORD_MAX} characters."
    elif new == current:
        errors["new"] = "New password must be different from the current one."

    if "new" not in errors and confirm != new:
        errors["confirm"] = "Passwords do not match."

    if errors:
        return render_template("settings.html", user=user, errors=errors, form={})

    user_model.update_password(user["id"], new)
    flash("Password changed.", "success")
    return redirect(url_for("shared.settings"))