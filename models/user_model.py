from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_db


def create(username, email, password, role="Student"):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, generate_password_hash(password), role),
    )
    db.commit()


def username_taken(username):
    return get_db().execute(
        "SELECT 1 FROM users WHERE lower(username) = lower(?)", (username,)
    ).fetchone() is not None


def email_taken(email):
    return get_db().execute(
        "SELECT 1 FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone() is not None


def authenticate(username, password):
    """Returns the user row if the login is correct, otherwise None."""
    user = get_db().execute(
        "SELECT * FROM users WHERE lower(username) = lower(?)", (username,)
    ).fetchone()
    if user and check_password_hash(user["password"], password):
        return user
    return None
