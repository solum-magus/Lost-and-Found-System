from database.connection import get_db


def create(user_id, name, category, description, location, item_status):
    """Saves a new report and returns its item_id."""
    db = get_db()
    cur = db.execute(
        "INSERT INTO items (user_id, name, category, description, location, item_status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, category, description, location, item_status),
    )
    db.commit()
    return cur.lastrowid


def get(item_id):
    return get_db().execute("SELECT * FROM items WHERE item_id = ?", (item_id,)).fetchone()


def by_user(user_id):
    return get_db().execute(
        "SELECT * FROM items WHERE user_id = ? ORDER BY item_id DESC", (user_id,)
    ).fetchall()

def search(text):
    """Active items whose name, category, location or description contains the text."""
    like = f"%{text}%"
    return get_db().execute(
        "SELECT * FROM items WHERE status = 'Active' AND "
        "(name LIKE ? OR category LIKE ? OR location LIKE ? OR description LIKE ?) "
        "ORDER BY item_id DESC",
        (like, like, like, like),
    ).fetchall()

def active_of_type(item_status, exclude_user_id):
    """Active items of one type ('Lost' or 'Found') reported by OTHER people."""
    return get_db().execute(
        "SELECT * FROM items WHERE item_status = ? AND status = 'Active' AND user_id != ?",
        (item_status, exclude_user_id),
    ).fetchall()

def set_status(item_id, status):
    """status is one of: Active, Claimed, Returned, Removed."""
    db = get_db()
    db.execute("UPDATE items SET status = ? WHERE item_id = ?", (status, item_id))
    db.commit()

def all_reports(item_status=None):
    """Every report from every user, newest first. Pass 'Lost' or 'Found' to filter."""
    if item_status in ("Lost", "Found"):
        return get_db().execute(
            "SELECT * FROM items WHERE item_status = ? ORDER BY item_id DESC", (item_status,)
        ).fetchall()
    return get_db().execute("SELECT * FROM items ORDER BY item_id DESC").fetchall()