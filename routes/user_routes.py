from flask import Blueprint, render_template

from routes.utils import login_required

bp = Blueprint("user", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("user/dashboard.html")


@bp.route("/items")
@login_required
def items():
    return render_template("user/items.html")


@bp.route("/claims")
@login_required
def claims():
    return render_template("user/claims.html")
