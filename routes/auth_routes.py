import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import user_model
from routes.utils import home_for

bp = Blueprint("auth", __name__)

# Rules Config
NAME_MIN, NAME_MAX = 2, 100
PASSWORD_MIN, PASSWORD_MAX = 8, 64
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for(home_for(session["role"])))
    return redirect(url_for("auth.signup"))      # first screen


def valid_name(name):
    """Letters (including ñ, é...), spaces, periods, hyphens and apostrophes only."""
    letters = sum(ch.isalpha() for ch in name)
    return letters >= 2 and all(ch.isalpha() or ch in " .'-" for ch in name)


def validate_signup(full_name, email, role, password, confirm):
    """Returns {field: message}. An empty dict means everything is valid."""
    errors = {}

    # Full name
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif not NAME_MIN <= len(full_name) <= NAME_MAX:
        errors["full_name"] = f"Full name must be {NAME_MIN} to {NAME_MAX} characters."
    elif not valid_name(full_name):
        errors["full_name"] = "Use letters, spaces, periods, hyphens and apostrophes only."

    # Email (this is also what they log in with)
    if not email:
        errors["email"] = "Email is required."
    elif len(email) > 100 or not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    elif user_model.email_taken(email):
        errors["email"] = "That email is already registered."

    # Role (Admin accounts can't be created from the signup form)
    if role not in ("Student", "Faculty"):
        errors["role"] = "Choose Student or Faculty."

    # Password
    if not password:
        errors["password"] = "Password is required."
    elif len(password) < PASSWORD_MIN:
        errors["password"] = f"Password must be at least {PASSWORD_MIN} characters."
    elif len(password) > PASSWORD_MAX:
        errors["password"] = f"Password must be at most {PASSWORD_MAX} characters."

    # Confirm (only worth checking if the password itself is fine)
    if "password" not in errors:
        if not confirm:
            errors["confirm"] = "Please confirm your password."
        elif confirm != password:
            errors["confirm"] = "Passwords do not match."

    return errors


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    errors = {}

    if request.method == "POST":
        full_name = " ".join(request.form.get("full_name", "").split())   # trims extra spaces
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "Student")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        errors = validate_signup(full_name, email, role, password, confirm)

        if not errors:
            user_model.create(full_name, email, password, role)
            flash("Account created. You can log in now.", "success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html", form=request.form, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    errors = {}

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email:
            errors["email"] = "Enter your email."
        if not password:
            errors["password"] = "Enter your password."

        if not errors:
            user = user_model.authenticate(email, password)
            if user and not user["is_active"]:
                # only shown after the password was correct, so it doesn't reveal who is registered
                errors["login"] = "This account is deactivated. Please contact an administrator."
            elif user:
                session.clear()
                session["user_id"] = user["id"]
                session["full_name"] = user["full_name"]
                session["role"] = user["role"]
                return redirect(url_for(home_for(user["role"])))   # admin or user side
            else:
                # Same message for a wrong email and a wrong password, on purpose,
                # so nobody can use the form to find out which emails are registered.
                errors["login"] = "Invalid email or password."

    return render_template("login.html", form=request.form, errors=errors)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))