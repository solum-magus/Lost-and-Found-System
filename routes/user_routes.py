from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import item_model, matching
from routes.utils import login_required
from database.connection import get_db

bp = Blueprint("user", __name__)

CATEGORIES = ["Electronics", "Wallet / Bag", "Keys", "ID / Cards", "Clothing",
              "Books / School supplies", "Other"]
TYPES = ["Lost", "Found"]

# DASHBOARD
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

# ITEMS
def validate_item(form):
    """Returns {field: message}. An empty dict means the form is valid."""
    errors = {}
    name = form["name"]

    if not name:
        errors["name"] = "Item name is required."
    elif not 2 <= len(name) <= 100:
        errors["name"] = "Item name must be 2 to 100 characters."

    if form["item_status"] not in TYPES:
        errors["item_status"] = "Choose Lost or Found."
    if form["category"] not in CATEGORIES:
        errors["category"] = "Choose a category."

    if not form["location"]:
        errors["location"] = "Location is required."
    elif len(form["location"]) > 100:
        errors["location"] = "Location must be at most 100 characters."

    if len(form["color"]) > 30:
        errors["color"] = "Color must be at most 30 characters."
    if len(form["description"]) > 500:
        errors["description"] = "Description must be at most 500 characters."

    return errors


@bp.route("/items", methods=["GET", "POST"])
@login_required
def items():
    errors = {}

    if request.method == "POST":
        # " ".join(x.split()) trims the ends and collapses repeated spaces
        form = {key: " ".join(request.form.get(key, "").split())
                for key in ("name", "item_status", "category", "color", "location", "description")}
        errors = validate_item(form)

        if not errors:
            item_id = item_model.create(session["user_id"], form["name"], form["category"],
                                        form["description"], form["color"], form["location"],
                                        form["item_status"])
            flash("Item reported.", "success")
            return redirect(url_for("user.item_matches", item_id=item_id))   # show matches next

    return render_template("user/items.html", categories=CATEGORIES, form=request.form,
                           errors=errors, my_items=item_model.by_user(session["user_id"]))

@bp.route("/items/<int:item_id>/remove", methods=["POST"])
@login_required
def remove_item(item_id):
    item = item_model.get(item_id)
    if item is None:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)                                   # you can only remove your own reports

    if item["status"] == "Active":
        item_model.set_status(item_id, "Removed")    # kept in the database, just not Active
        flash("Report removed.", "success")
    return redirect(url_for("user.items"))

@bp.route("/items/<int:item_id>/matches")
@login_required
def item_matches(item_id):
    item = item_model.get(item_id)
    if item is None:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)                                   # only the reporter sees their matches

    # A Lost item is compared with Found items, and a Found item with Lost items
    opposite = "Found" if item["item_status"] == "Lost" else "Lost"
    candidates = item_model.active_of_type(opposite, session["user_id"])
    matches = matching.find_matches(item, candidates)

    return render_template("user/item_matches.html", item=item, matches=matches,
                           opposite=opposite, my_words=sorted(matching.item_words(item)))


@bp.route("/claims")
@login_required
def claims():
    return render_template("user/claims.html")