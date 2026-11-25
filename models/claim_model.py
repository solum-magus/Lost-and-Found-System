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
        "WHERE claims.user_id = ? ORDER BY claims.claim_id DESC",
        (user_id,),
    ).fetchall()


def has_pending(item_id, user_id):
    """True if this user already has a Pending claim on this item."""
    return get_db().execute(
        "SELECT 1 FROM claims WHERE item_id = ? AND user_id = ? AND claim_status = 'Pending'",
        (item_id, user_id),
    ).fetchone() is not None