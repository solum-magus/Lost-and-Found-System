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