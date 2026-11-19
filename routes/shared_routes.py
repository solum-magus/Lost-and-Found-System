from flask import Blueprint, render_template

from routes.utils import login_required

bp = Blueprint("shared", __name__)

# History and Settings are used by both roles. Each role's sidebar links here,
# and the sidebar shown is decided in base.html from session.role.


@bp.route("/history")
@login_required
def history():
    return render_template("history.html")


@bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")
