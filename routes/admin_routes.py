from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import claim_model, item_model, user_model
from routes.utils import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    all_items = item_model.all_with_reporter()
    all_claims = claim_model.all_with_names()

    # Counts for the cards (from the full lists, not just the 5 shown)
    lost_count = sum(1 for i in all_items if i["item_status"] == "Lost")
    found_count = sum(1 for i in all_items if i["item_status"] == "Found")
    pending_count = sum(1 for c in all_claims if c["claim_status"] == "Pending")
    approved_count = sum(1 for c in all_claims if c["claim_status"] == "Approved")
    rejected_count = sum(1 for c in all_claims if c["claim_status"] == "Rejected")
    resolved_count = approved_count + rejected_count

    monday = date.today() - timedelta(days=date.today().weekday())
    week_days = [monday + timedelta(days=n) for n in range(6)]
    chart_labels = [d.strftime("%A") for d in week_days]            # "Monday", "Tuesday", ...
    found_data = []
    lost_data = []
    for d in week_days:
        day = d.isoformat()                                         # "2026-11-23", same format as date_reported
        found_data.append(sum(1 for i in all_items if i["date_reported"] == day and i["item_status"] == "Found"))
        lost_data.append(sum(1 for i in all_items if i["date_reported"] == day and i["item_status"] == "Lost"))

    return render_template(
        "admin/dashboard.html",
        full_name=session["full_name"],
        role=session["role"],
        all_items=all_items[:5],        # only the 5 newest are shown; the counts above use all of them
        all_claims=all_claims[:5],
        lost_count=lost_count,
        found_count=found_count,
        pending_count=pending_count,
        resolved_count=resolved_count,
        chart_labels=chart_labels,
        found_data=found_data,
        lost_data=lost_data,
        approved_count=approved_count,
        rejected_count=rejected_count,
    )


# ---------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------
@bp.route("/users")
@admin_required
def users():
    # Every report and every claim, once. They are grouped per user below.
    items_by_user = {}
    for item in item_model.all_reports():
        items_by_user.setdefault(item["user_id"], []).append(item)
    claims_by_user = {}
    for claim in claim_model.all_with_item_name():
        claims_by_user.setdefault(claim["user_id"], []).append(claim)

    return render_template(
        "admin/users.html",
        all_users=user_model.all_with_counts(),
        items_by_user=items_by_user,
        claims_by_user=claims_by_user,
        my_id=session["user_id"],
    )


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def update_role(user_id):
    new_role = request.form.get("role", "")

    if user_id == session["user_id"]:
        flash("You can't change your own role.", "warning")
        return redirect(url_for("admin.users"))

    if new_role != "Student" and new_role != "Faculty" and new_role != "Admin":
        flash("Invalid role.", "warning")
        return redirect(url_for("admin.users"))

    user_model.set_role(user_id, new_role)

    flash("User role updated.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/status", methods=["POST"])
@admin_required
def update_status(user_id):
    """Deactivate or reactivate an account. Nothing is deleted, so reports and claims stay."""
    if user_id == session["user_id"]:
        flash("You can't deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))

    if user_model.get_by_id(user_id) is None:
        flash("User not found.", "warning")
        return redirect(url_for("admin.users"))

    if request.form.get("action") == "reactivate":
        user_model.set_active(user_id, True)
        flash("User reactivated. They can log in again.", "success")
    else:
        user_model.set_active(user_id, False)
        flash("User deactivated. They can no longer log in.", "success")

    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------
# CLAIMS
# ---------------------------------------------------------------
@bp.route("/claims")
@admin_required
def claims():
    return render_template("admin/claims.html", all_claims=claim_model.all_with_details())


def get_note():
    """The admin's message from the form (where to claim, or why rejected).
    Returns (note, error). Exactly one of them is None."""
    note = request.form.get("admin_note", "").strip()
    if len(note) < 3 or len(note) > 300:
        return None, "Please write a message of 3 to 300 characters."
    return note, None


@bp.route("/claims/<int:claim_id>/approve", methods=["POST"])
@admin_required
def approve_claim(claim_id):
    note, error = get_note()
    if error:
        flash("To approve, tell the claimant where to get the item. " + error, "warning")
        return redirect(url_for("admin.claims"))

    claim = claim_model.get(claim_id)
    if claim is None:
        flash("Claim not found.", "warning")
        return redirect(url_for("admin.claims"))

    if claim["claim_status"] != "Pending":
        flash("Only pending claims can be approved.", "warning")
        return redirect(url_for("admin.claims"))

    item = item_model.get(claim["item_id"])
    if item is None or item["status"] != "Active":
        flash("This item is no longer active, so the claim can't be approved.", "warning")
        return redirect(url_for("admin.claims"))

    claim_model.approve(claim_id, claim["item_id"], note)

    flash("Claim approved. Other pending claims on this item were rejected.", "success")
    return redirect(url_for("admin.claims"))


@bp.route("/claims/<int:claim_id>/reject", methods=["POST"])
@admin_required
def reject_claim(claim_id):
    note, error = get_note()
    if error:
        flash("To reject, give a reason. " + error, "warning")
        return redirect(url_for("admin.claims"))

    claim = claim_model.get(claim_id)
    if claim is None:
        flash("Claim not found.", "warning")
        return redirect(url_for("admin.claims"))

    if claim["claim_status"] != "Pending":
        flash("Only pending claims can be rejected.", "warning")
        return redirect(url_for("admin.claims"))

    claim_model.reject(claim_id, note)

    flash("Claim rejected.", "success")
    return redirect(url_for("admin.claims"))