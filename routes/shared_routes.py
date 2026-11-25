from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from models import claim_model, item_model, user_model
from routes.auth_routes import (EMAIL_RE, NAME_MAX, NAME_MIN, PASSWORD_MAX,
                                PASSWORD_MIN, valid_name)
from routes.utils import login_required

bp = Blueprint("shared", __name__)

@bp.route("/reports")
@login_required
def reports():
    q = " ".join(request.args.get("q", "").split())      # text typed in the top bar search
    kind = request.args.get("type", "")                  # "Lost", "Found", "Mine", or anything else = all

    if kind == "Mine" and session["role"] != "Admin":
        # Everything this user reported (any status) and every claim they made
        def has_q(*fields):
            return q.lower() in " ".join(f or "" for f in fields).lower()

        my_reports = [i for i in item_model.by_user(session["user_id"])
                      if has_q(i["name"], i["category"], i["location"], i["description"])]
        my_claims = [c for c in claim_model.by_user(session["user_id"])
                     if has_q(c["item_name"], c["proof_description"])]
        return render_template("reports.html", q=q, kind="Mine",
                               my_reports=my_reports, my_claims=my_claims)

    # Admins see every report, whatever its status; everyone else sees only Active ones
    results = item_model.search(q, include_all=session["role"] == "Admin")   # empty q = everything                      # empty q = everything

    # Counts for the tabs always come from the full result, before the Lost/Found filter
    counts = {"All": len(results),
              "Lost": sum(1 for r in results if r["item_status"] == "Lost"),
              "Found": sum(1 for r in results if r["item_status"] == "Found")}

    if kind in ("Lost", "Found"):
        results = [r for r in results if r["item_status"] == kind]
    else:
        kind = "All"

    return render_template("reports.html", q=q, kind=kind, counts=counts, results=results)


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