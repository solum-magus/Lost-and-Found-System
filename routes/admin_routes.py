from flask import Blueprint, render_template

from routes.utils import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@bp.route("/claims")
@admin_required
def claims():
    return render_template("admin/claims.html")


@bp.route("/users")
@admin_required
def users():
    return render_template("admin/users.html")
