from typing import Callable, TypeVar
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

from functools import wraps
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user  #
from werkzeug import Response

from app.model.user import User
from app.auth.forms import LoginForm, SigninForm

bp = Blueprint("auth", __name__)


def logged_out(func: Callable[P, R]) -> Callable[P, R | Response]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | Response:
        if current_user.is_authenticated:
            return redirect(url_for("index.home_page"))
        return func(*args, **kwargs)

    return wrapper


@bp.route("/login", methods=["GET", "POST"])
@logged_out
def login() -> str | Response:
    form = LoginForm()
    if form.validate_on_submit():
        next: str | None = request.args.get("next")
        if user := User.authenticate(form.email.data, form.password.data):  # type: ignore # form data is valid at this point
            login_user(user, remember=form.remember_me.data)
            return redirect(next or url_for("index.home_page"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("auth.login", next=next))
    return render_template("auth/login.html", form=form)


@bp.route("/signin", methods=["GET", "POST"])
@logged_out
def signin() -> str | Response:
    form = SigninForm()
    if form.validate_on_submit():
        # Add signin logic here
        if not User.get_user_by_email(form.email.data):  # type: ignore # form data is valid at this point
            new_user = User.create(form.username.data, form.email.data, form.password.data)  # type: ignore # form data is valid at this point
            login_user(new_user, remember=form.remember_me.data)
            return redirect(url_for("index.home_page"))
        else:
            flash("Email already exists")
            return redirect(url_for("auth.signin"))
    return render_template("auth/signin.html", form=form)


@bp.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("auth.login"))
