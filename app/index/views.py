from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("index", __name__)


@bp.route("/")
@login_required
def home_page() -> str:
    return render_template("index/index.html")


@bp.route("/home")
@login_required
def home() -> str:
    return render_template("index/home.html")
