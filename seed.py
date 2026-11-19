"""Adds a test admin and a test student. Safe to run more than once.

    python seed.py
"""
from app import create_app
from models import user_model

ACCOUNTS = [
    ("admin", "admin@plv.edu.ph", "admin123", "Admin"),
    ("student", "student@plv.edu.ph", "user123", "Student"),
]

app = create_app()

with app.app_context():
    for username, email, password, role in ACCOUNTS:
        if user_model.username_taken(username):
            print("Skipped (already exists):", username)
        else:
            user_model.create(username, email, password, role)
            print(f"Added: {username} / {password} ({role})")
