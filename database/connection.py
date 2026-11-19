import sqlite3
from flask import current_app, g

path = "database/plv-laf.db"

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        create_tables()

def get_db():
    """One connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def create_tables():

    get_db().execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Student'
                CHECK(role IN ('Student', 'Faculty', 'Admin'))
        )
    ''')

    get_db().execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            color TEXT,
            location TEXT NOT NULL,
            item_status TEXT NOT NULL
                CHECK(item_status IN ('Lost', 'Found')),
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active', 'Claimed', 'Returned', 'Removed')),
            date_reported DATE NOT NULL DEFAULT CURRENT_DATE,

            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    get_db().execute('''
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            proof_description TEXT NOT NULL,
            claim_date DATE NOT NULL DEFAULT CURRENT_DATE,
            claim_status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(claim_status IN ('Pending', 'Approved', 'Rejected')),

            FOREIGN KEY (item_id) REFERENCES items (item_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')