from database.connection import get_db
from datetime import date

def create(item_id, user_id, proof_description):
    """Saves a new claim (status starts as 'Pending') and returns its claim_id."""
    db = get_db()
    cur = db.execute(
        "INSERT INTO claims (item_id, user_id, proof_description, claim_date) VALUES (?, ?, ?, ?)",
        (item_id, user_id, proof_description, date.today().isoformat()),
    )
    db.commit()
    return cur.lastrowid


def by_user(user_id):
    """All claims made by one user, newest first, with the item's name."""
    return get_db().execute(
        "SELECT claims.*, items.name AS item_name "
        "FROM claims JOIN items ON claims.item_id = items.item_id "
        "WHERE claims.user_id = ? ORDER BY claims.claim_date DESC, claims.claim_id DESC",
        (user_id,),
    ).fetchall()


def has_pending(item_id, user_id):
    """True if this user already has a Pending claim on this item."""
    return get_db().execute(
        "SELECT 1 FROM claims WHERE item_id = ? AND user_id = ? AND claim_status = 'Pending'",
        (item_id, user_id),
    ).fetchone() is not None

def get(claim_id):
    return get_db().execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,)).fetchone()


def all_with_names():
    """Every claim with the item name and claimant name, newest first (admin dashboard)."""
    return get_db().execute(
        "SELECT claims.claim_id, claims.item_id, claims.user_id AS claimant_id, claims.proof_description, "
        "claims.claim_date, claims.claim_status, "
        "items.name AS item_name, users.full_name AS claimant "
        "FROM claims JOIN items ON claims.item_id = items.item_id "
        "JOIN users ON claims.user_id = users.id "
        "ORDER BY claims.claim_date DESC, claims.claim_id DESC"
    ).fetchall()


def all_with_item_name():
    """Every claim with its item's name, newest first (admin Users page)."""
    return get_db().execute(
        "SELECT claims.claim_id, claims.user_id, claims.item_id, claims.proof_description, "
        "claims.claim_date, claims.claim_status, claims.admin_note, items.name AS item_name "
        "FROM claims JOIN items ON claims.item_id = items.item_id "
        "ORDER BY claims.claim_id DESC"
    ).fetchall()


def all_with_details():
    """Every claim with claimant, item and finder info; Pending first (admin Claims page)."""
    return get_db().execute(
        "SELECT claims.claim_id, claims.item_id, claims.user_id AS claimant_id, "
        "claims.proof_description, claims.claim_date, claims.claim_status, claims.admin_note, "
        "claimant.full_name AS claimant, claimant.email AS claimant_email, "
        "items.name AS item_name, items.category, items.location, items.description, "
        "items.item_status, items.status AS item_state, items.date_reported, "
        "finder.full_name AS finder, finder.email AS finder_email "
        "FROM claims "
        "JOIN items ON claims.item_id = items.item_id "
        "JOIN users AS claimant ON claims.user_id = claimant.id "
        "JOIN users AS finder ON items.user_id = finder.id "
        "ORDER BY (claims.claim_status = 'Pending') DESC, "
        "claims.claim_date DESC, claims.claim_id DESC"
    ).fetchall()


def approve(claim_id, item_id, note):
    """Approves one claim, marks the item Claimed and rejects the other pending claims on it."""
    db = get_db()
    db.execute(
        "UPDATE claims SET claim_status = 'Approved', admin_note = ? WHERE claim_id = ?",
        (note, claim_id),
    )
    db.execute("UPDATE items SET status = 'Claimed' WHERE item_id = ?", (item_id,))
    db.execute(
        "UPDATE claims SET claim_status = 'Rejected', "
        "admin_note = 'Another claim on this item was approved.' "
        "WHERE item_id = ? AND claim_id != ? AND claim_status = 'Pending'",
        (item_id, claim_id),
    )
    db.commit()


def reject(claim_id, note):
    db = get_db()
    db.execute(
        "UPDATE claims SET claim_status = 'Rejected', admin_note = ? WHERE claim_id = ?",
        (note, claim_id),
    )
    db.commit()

def reject_pending_for_item(item_id, note):
    """Rejects every Pending claim on an item, with a reason (used when its report is removed)."""
    db = get_db()
    db.execute(
        "UPDATE claims SET claim_status = 'Rejected', admin_note = ? "
        "WHERE item_id = ? AND claim_status = 'Pending'",
        (note, item_id),
    )
    db.commit()