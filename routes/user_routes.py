from flask import Blueprint, render_template, session

from database.connection import get_db
from routes.utils import login_required

bp = Blueprint("user", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]

    # Items this user reported (newest first)
    my_items = db.execute(
        "SELECT item_id, name, category, location, item_status, status, date_reported "
        "FROM items WHERE user_id = ? ORDER BY date_reported DESC, item_id DESC",
        (user_id,),
    ).fetchall()

    # Claims this user made, with the name of the item claimed
    my_claims = db.execute(
        "SELECT claims.claim_id, claims.claim_date, claims.claim_status, items.name "
        "FROM claims JOIN items ON claims.item_id = items.item_id "
        "WHERE claims.user_id = ? ORDER BY claims.claim_date DESC, claims.claim_id DESC",
        (user_id,),
    ).fetchall()

    # Simple counts for the summary cards
    lost_count = 0
    found_count = 0
    for item in my_items:
        if item["item_status"] == "Lost":
            lost_count = lost_count + 1
        else:
            found_count = found_count + 1

    pending_count = 0
    for claim in my_claims:
        if claim["claim_status"] == "Pending":
            pending_count = pending_count + 1

    return render_template(
        "user/dashboard.html",
        full_name=session["full_name"],
        role=session["role"],
        my_items=my_items,
        my_claims=my_claims,
        lost_count=lost_count,
        found_count=found_count,
        pending_count=pending_count,
    )


@bp.route("/items")
@login_required
def items():
    return render_template("user/items.html")


@bp.route("/claims")
@login_required
def claims():
    return render_template("user/claims.html")