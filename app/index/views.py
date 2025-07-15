from flask import Blueprint, redirect, url_for
from flask_login import login_required

bp = Blueprint("index", __name__)


@bp.route("/")
@login_required
def home_page() -> str:
    return redirect(url_for("user.user_dashboard"))
