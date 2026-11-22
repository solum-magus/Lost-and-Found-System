from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import claim_model, item_model, matching
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
                for key in ("name", "item_status", "category", "location", "description")}
        errors = validate_item(form)

        if not errors:
            item_id = item_model.create(session["user_id"], form["name"], form["category"],
                                        form["description"], form["location"],
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


# CLAIMS
def validate_claim(form):
    """Returns (errors, item). An empty errors dict means the form is valid."""
    errors = {}
    item = None

    if not form["item_id"].isdigit():
        errors["item_id"] = "Enter a valid item ID (numbers only)."
    else:
        item = item_model.get(int(form["item_id"]))
        if item is None:
            errors["item_id"] = "No item with that ID."
        elif item["item_status"] != "Found":
            errors["item_id"] = "Only items reported as Found can be claimed."
        elif item["status"] != "Active":
            errors["item_id"] = "This item is no longer available to claim."
        elif item["user_id"] == session["user_id"]:
            errors["item_id"] = "You can't claim an item you reported yourself."
        elif claim_model.has_pending(item["item_id"], session["user_id"]):
            errors["item_id"] = "You already have a pending claim on this item."

    proof = form["proof_description"]
    if not proof:
        errors["proof_description"] = "Please describe how you can prove this is yours."
    elif not 10 <= len(proof) <= 500:
        errors["proof_description"] = "Proof must be 10 to 500 characters."

    return errors, item


@bp.route("/claims", methods=["GET", "POST"])
@login_required
def claims():
    errors = {}
    form = {"item_id": request.args.get("item_id", "").strip(), "proof_description": ""}  # ?item_id=5 prefills

    if request.method == "POST":
        form = {key: " ".join(request.form.get(key, "").split())
                for key in ("item_id", "proof_description")}
        errors, item = validate_claim(form)

        if not errors:
            claim_model.create(item["item_id"], session["user_id"], form["proof_description"])
            flash("Claim submitted. Please wait for the admin to review it.", "success")
            return redirect(url_for("user.claims"))

    # show the item's details next to the form once a valid ID is typed / passed in the link
    item_preview = item_model.get(int(form["item_id"])) if form["item_id"].isdigit() else None

    return render_template("user/claims.html", form=form, errors=errors, item=item_preview,
                           my_claims=claim_model.by_user(session["user_id"]))