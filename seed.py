"""Create repeatable demonstration accounts, reports, and claims.
Run with: python seed.py
Remove demonstration records before deployment.
"""
from datetime import date, timedelta

from app import create_app
from database.connection import get_db
from models import user_model

ACCOUNTS = [
    ("System Admin", "admin@plv.edu.ph", "admin123", "Admin"),
    ("Alex Santos", "student1@plv.edu.ph", "student123", "Student"),
    ("Bea Reyes", "student2@plv.edu.ph", "student123", "Student"),
    ("Carlos Garcia", "student3@plv.edu.ph", "student123", "Student"),
    ("Diana Cruz", "student4@plv.edu.ph", "student123", "Student"),
    ("Ethan Flores", "student5@plv.edu.ph", "student123", "Student"),
    ("Faith Mendoza", "student6@plv.edu.ph", "student123", "Student"),
    ("Gabriel Lim", "faculty1@plv.edu.ph", "faculty123", "Faculty"),
    ("Hannah Torres", "faculty2@plv.edu.ph", "faculty123", "Faculty"),
    ("Ivan Bautista", "student7@plv.edu.ph", "student123", "Student"),
]

# owner email, item name, category, description, location, type, status, days ago
ITEMS = [
    ("student1@plv.edu.ph", "Black wireless earbuds", "Electronics", "Small black earbuds in a charging case.", "Library, 2nd floor", "Lost", "Active", 1),
    ("student2@plv.edu.ph", "Blue Jansport backpack", "Wallet / Bag", "Blue backpack with notebooks inside.", "Cafeteria", "Found", "Active", 1),
    ("student3@plv.edu.ph", "Student ID card", "ID / Cards", "ID card in a clear plastic holder.", "Main building, Room 204", "Found", "Claimed", 3),
    ("student4@plv.edu.ph", "Silver water bottle", "Other", "Insulated silver bottle with stickers.", "Gymnasium", "Lost", "Active", 2),
    ("student5@plv.edu.ph", "Scientific calculator", "Electronics", "Casio scientific calculator.", "Math building, Room 105", "Lost", "Active", 4),
    ("faculty1@plv.edu.ph", "Set of classroom keys", "Keys", "Three keys on a red keychain.", "Faculty room", "Found", "Active", 2),
    ("student6@plv.edu.ph", "Black rectangular eyeglasses", "Other", "Black frame inside a soft case.", "AVR", "Found", "Returned", 5),
    ("student7@plv.edu.ph", "PE uniform jacket", "Clothing", "Navy blue jacket with initials on the tag.", "Covered court", "Lost", "Active", 6),
    ("faculty2@plv.edu.ph", "USB flash drive", "Electronics", "32GB silver USB drive.", "Computer laboratory 1", "Found", "Active", 3),
    ("student2@plv.edu.ph", "Literature textbook", "Books / School supplies", "English literature textbook with handwritten notes.", "Library, ground floor", "Lost", "Active", 7),
    ("student3@plv.edu.ph", "Brown leather wallet", "Wallet / Bag", "Brown wallet containing cards; no cash mentioned.", "Registrar hallway", "Found", "Active", 8),
    ("student5@plv.edu.ph", "Pink umbrella", "Other", "Foldable pink umbrella.", "Gate entrance", "Found", "Active", 9),
    ("student1@plv.edu.ph", "Yellow notebook", "Books / School supplies", "Yellow spiral notebook for programming.", "Computer laboratory 2", "Lost", "Active", 10),
    ("faculty1@plv.edu.ph", "Power adapter", "Electronics", "Laptop power adapter left near the podium.", "Lecture hall", "Found", "Active", 11),
    ("student4@plv.edu.ph", "Black ball cap", "Clothing", "Plain black cap.", "Student lounge", "Lost", "Active", 12),
]

# item name, claimant email, proof, status, admin note, days ago
CLAIMS = [
    ("Student ID card", "student1@plv.edu.ph", "The name and student number on the card are mine.", "Approved", "Please claim it at the Admin Office.", 2),
    ("Black rectangular eyeglasses", "student2@plv.edu.ph", "I can identify the brand and the case design.", "Approved", "Returned to the owner at the Admin Office.", 4),
    ("Blue Jansport backpack", "student4@plv.edu.ph", "There is a blue notebook and a keychain inside.", "Pending", None, 1),
    ("Set of classroom keys", "faculty2@plv.edu.ph", "One key has a small blue tag attached.", "Pending", None, 1),
    ("USB flash drive", "student6@plv.edu.ph", "It contains my class presentation files.", "Rejected", "The details provided did not match the item.", 2),
    ("Brown leather wallet", "student7@plv.edu.ph", "I can identify the cards and the wallet brand.", "Pending", None, 3),
    ("Power adapter", "student3@plv.edu.ph", "It is the adapter for my laptop; I can identify its model.", "Rejected", "Ownership could not be verified.", 5),
]

app = create_app()
with app.app_context():
    db = get_db()

    # Migrate older copies of the database without deleting existing records.
    user_columns = {r["name"] for r in db.execute("PRAGMA table_info(users)")}
    if "is_active" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
    claim_columns = {r["name"] for r in db.execute("PRAGMA table_info(claims)")}
    if "admin_note" not in claim_columns:
        db.execute("ALTER TABLE claims ADD COLUMN admin_note TEXT")
    db.commit()

    user_ids = {}
    for full_name, email, password, role in ACCOUNTS:
        if not user_model.email_taken(email):
            user_model.create(full_name, email, password, role)
            print("Added account:", email)
        else:
            print("Existing account:", email)
        user_ids[email] = db.execute("SELECT id FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()["id"]

    item_ids = {}
    for owner_email, name, category, description, location, kind, status, days_ago in ITEMS:
        existing = db.execute(
            "SELECT item_id FROM items WHERE user_id=? AND name=? AND location=?",
            (user_ids[owner_email], name, location),
        ).fetchone()
        if existing:
            item_id = existing["item_id"]
        else:
            reported = (date.today() - timedelta(days=days_ago)).isoformat()
            cur = db.execute(
                "INSERT INTO items (user_id,name,category,description,location,item_status,status,date_reported) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (user_ids[owner_email], name, category, description, location, kind, status, reported),
            )
            item_id = cur.lastrowid
            print("Added report:", name)
        item_ids[name] = item_id

    for item_name, claimant_email, proof, status, note, days_ago in CLAIMS:
        item_id = item_ids[item_name]
        exists = db.execute(
            "SELECT 1 FROM claims WHERE item_id=? AND user_id=? AND proof_description=?",
            (item_id, user_ids[claimant_email], proof),
        ).fetchone()
        if not exists:
            claim_date = (date.today() - timedelta(days=days_ago)).isoformat()
            db.execute(
                "INSERT INTO claims (item_id,user_id,proof_description,claim_date,claim_status,admin_note) "
                "VALUES (?,?,?,?,?,?)",
                (item_id, user_ids[claimant_email], proof, claim_date, status, note),
            )
            print("Added claim:", item_name, "->", status)

    db.commit()
    print("\nDemo data ready:")
    print("Accounts:", db.execute("SELECT COUNT(*) FROM users").fetchone()[0])
    print("Reports:", db.execute("SELECT COUNT(*) FROM items").fetchone()[0])
    print("Claims:", db.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
    print("Database:", app.config["DATABASE"])
    print("\nDemo passwords: admin123 for admin; student123 for student accounts; faculty123 for faculty accounts.")
