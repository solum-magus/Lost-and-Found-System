from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from database.connection import get_db
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


# ---------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------
@bp.route("/users")
@admin_required
def users():
    db = get_db()
    all_users = db.execute(
        "SELECT users.id, users.full_name, users.email, users.role, "
        "(SELECT COUNT(*) FROM items WHERE items.user_id = users.id) AS item_count, "
        "(SELECT COUNT(*) FROM claims WHERE claims.user_id = users.id) AS claim_count "
        "FROM users ORDER BY users.full_name"
    ).fetchall()

    return render_template(
        "admin/users.html",
        all_users=all_users,
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

    db = get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()

    flash("User role updated.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == session["user_id"]:
        flash("You can't delete your own account.", "warning")
        return redirect(url_for("admin.users"))

    db = get_db()

    item_count = db.execute(
        "SELECT COUNT(*) FROM items WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    claim_count = db.execute(
        "SELECT COUNT(*) FROM claims WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    if item_count > 0 or claim_count > 0:
        flash("This user has items or claims, so they can't be deleted.", "warning")
        return redirect(url_for("admin.users"))

    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()

    flash("User deleted.", "success")
    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------
# CLAIMS MANAGEMENT
# ---------------------------------------------------------------
@bp.route("/claims")
@admin_required
def claims():
    db = get_db()
    all_claims = db.execute(
        "SELECT claims.claim_id, claims.proof_description, claims.claim_date, "
        "claims.claim_status, items.name AS item_name, items.status AS item_state, "
        "users.full_name AS claimant, users.email AS claimant_email "
        "FROM claims "
        "JOIN items ON claims.item_id = items.item_id "
        "JOIN users ON claims.user_id = users.id "
        "ORDER BY (claims.claim_status = 'Pending') DESC, "
        "claims.claim_date DESC, claims.claim_id DESC"
    ).fetchall()

    return render_template("admin/claims.html", all_claims=all_claims)


@bp.route("/claims/<int:claim_id>/approve", methods=["POST"])
@admin_required
def approve_claim(claim_id):
    db = get_db()
    claim = db.execute(
        "SELECT claim_id, item_id, claim_status FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()

    if claim is None:
        flash("Claim not found.", "warning")
        return redirect(url_for("admin.claims"))

    if claim["claim_status"] != "Pending":
        flash("Only pending claims can be approved.", "warning")
        return redirect(url_for("admin.claims"))

    item = db.execute(
        "SELECT status FROM items WHERE item_id = ?", (claim["item_id"],)
    ).fetchone()

    if item is None or item["status"] != "Active":
        flash("This item is no longer active, so the claim can't be approved.", "warning")
        return redirect(url_for("admin.claims"))

    # 1. Approve this claim
    db.execute(
        "UPDATE claims SET claim_status = 'Approved' WHERE claim_id = ?",
        (claim_id,),
    )
    # 2. Mark the item as claimed
    db.execute(
        "UPDATE items SET status = 'Claimed' WHERE item_id = ?",
        (claim["item_id"],),
    )
    # 3. Reject the other pending claims on the same item
    db.execute(
        "UPDATE claims SET claim_status = 'Rejected' "
        "WHERE item_id = ? AND claim_id != ? AND claim_status = 'Pending'",
        (claim["item_id"], claim_id),
    )
    db.commit()

    flash("Claim approved. Other pending claims on this item were rejected.", "success")
    return redirect(url_for("admin.claims"))


@bp.route("/claims/<int:claim_id>/reject", methods=["POST"])
@admin_required
def reject_claim(claim_id):
    db = get_db()
    claim = db.execute(
        "SELECT claim_id, claim_status FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()

    if claim is None:
        flash("Claim not found.", "warning")
        return redirect(url_for("admin.claims"))

    if claim["claim_status"] != "Pending":
        flash("Only pending claims can be rejected.", "warning")
        return redirect(url_for("admin.claims"))

    db.execute(
        "UPDATE claims SET claim_status = 'Rejected' WHERE claim_id = ?",
        (claim_id,),
    )
    db.commit()

    flash("Claim rejected.", "success")
    return redirect(url_for("admin.claims"))
