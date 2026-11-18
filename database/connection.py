import sqlite3

path = "database/plv-laf.db"

def create_connection():
    return sqlite3.connect(path)

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Student'
                CHECK(role IN ('Student', 'Faculty', 'Admin'))
        )
    ''')

    cursor.execute('''
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

    cursor.execute('''
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

    conn.commit()
    conn.close()