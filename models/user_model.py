from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_db

def create(full_name, email, password, role="Student"):
    db = get_db()
    db.execute(
        "INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
        (full_name, email, generate_password_hash(password), role),
    )
    db.commit()


def email_taken(email):
    return get_db().execute(
        "SELECT 1 FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone() is not None


def authenticate(email, password):
    """Returns the user row if the login is correct, otherwise None."""
    user = get_db().execute(
        "SELECT * FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    if user and check_password_hash(user["password"], password):
        return user
    return None

def get_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def email_taken_by_other(email, user_id):
    """True if someone ELSE already uses this email (your own email doesn't count)."""
    return get_db().execute(
        "SELECT 1 FROM users WHERE lower(email) = lower(?) AND id != ?", (email, user_id)
    ).fetchone() is not None


def update_profile(user_id, full_name, email):
    db = get_db()
    db.execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?", (full_name, email, user_id))
    db.commit()


def update_password(user_id, new_password):
    db = get_db()
    db.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(new_password), user_id))
    db.commit()

def set_active(user_id, active):
    """active=True re-enables the account, active=False deactivates it (nothing is deleted)."""
    db = get_db()
    db.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if active else 0, user_id))
    db.commit()

def all_with_counts():
    """Every user with how many reports and claims they have (admin Users page)."""
    return get_db().execute(
        "SELECT users.id, users.full_name, users.email, users.role, users.is_active, "
        "(SELECT COUNT(*) FROM items WHERE items.user_id = users.id) AS item_count, "
        "(SELECT COUNT(*) FROM claims WHERE claims.user_id = users.id) AS claim_count "
        "FROM users ORDER BY users.full_name"
    ).fetchall()

def set_role(user_id, role):
    db = get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    db.commit()