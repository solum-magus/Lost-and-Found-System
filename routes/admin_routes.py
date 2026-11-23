from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from routes.utils import admin_required
from database.connection import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]

    # Items
    all_items = db.execute(
        "SELECT item_id, user_id, name, category, location, item_status, status, date_reported "
        "FROM items ORDER BY date_reported DESC, item_id DESC"
    ).fetchall()

    # Claims
    all_claims = db.execute(
        "SELECT claims.claim_id, claims.claim_date, claims.claim_status, items.name "
        "FROM claims JOIN items ON claims.item_id = items.item_id "
        "ORDER BY claims.claim_date DESC, claims.claim_id DESC"
    ).fetchall()

    # Counts for Cards
    lost_count = 0
    found_count = 0
    for item in all_items:
        if item["item_status"] == "Lost":
            lost_count = lost_count + 1
        else:
            found_count = found_count + 1

    pending_count = 0
    for claim in all_claims:
        if claim["claim_status"] == "Pending":
            pending_count = pending_count + 1

    resolved_count = 0
    for claim in all_claims:
        if claim["claim_status"] == "Approved":
            resolved_count = resolved_count + 1
        if claim["claim_status"] == "Rejected":
            resolved_count = resolved_count + 1

    return render_template(
        "admin/dashboard.html",
        full_name=session["full_name"],
        role=session["role"],
        all_items=all_items,
        all_claims=all_claims,
        lost_count=lost_count,
        found_count=found_count,
        pending_count=pending_count,
        resolved_count=resolved_count
    )


@bp.route("/claims")
@admin_required
def claims():
    return render_template("admin/claims.html")


@bp.route("/users")
@admin_required
def users():
    return render_template("admin/users.html")
