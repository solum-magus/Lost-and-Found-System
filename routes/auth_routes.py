from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import user_model
from routes.utils import home_for

bp = Blueprint("auth", __name__)


@bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for(home_for(session["role"])))
    return redirect(url_for("auth.signup"))      # first screen, like the Tkinter app


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "Student")
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
        elif role not in ("Student", "Faculty"):
            flash("Choose Student or Faculty.", "danger")
        elif user_model.username_taken(username):
            flash("That username is already taken.", "danger")
        elif user_model.email_taken(email):
            flash("That email is already registered.", "danger")
        else:
            user_model.create(username, email, password, role)
            flash("Account created. You can log in now.", "success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = user_model.authenticate(request.form.get("username", "").strip(),
                                       request.form.get("password", ""))
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for(home_for(user["role"])))   # admin or user side

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
