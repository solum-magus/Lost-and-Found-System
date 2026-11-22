"""(Remove before demonstration) Adds a test admin and a test student. Safe to run more than once."""
from app import create_app
from database.connection import get_db
from models import user_model

ACCOUNTS = [
    ("System Admin", "admin@plv.edu.ph", "admin123", "Admin"),
    ("PLV Student", "student@plv.edu.ph", "student123", "Student"),
    ("Faculty Staff", "faculty@plv.edu.ph", "faculty123", "Faculty")
]

app = create_app()

with app.app_context():
    for full_name, email, password, role in ACCOUNTS:
        if user_model.email_taken(email):
            print("Skipped (already exists):", email)
        else:
            user_model.create(full_name, email, password, role)
            print(f"Added: {full_name} | log in with {email} / {password} ({role})")

    print("\nid | full_name | email | role")
    for row in get_db().execute("SELECT id, full_name, email, role FROM users ORDER BY id"):
        print(f"{row['id']} | {row['full_name']} | {row['email']} | {row['role']}")