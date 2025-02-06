from functools import wraps
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user

from app.database import db
from app.model.user import User
from app.auth.forms import LoginForm, SigninForm


bp = Blueprint("auth", __name__)


def logged_out(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("index.home_page"))
        return func(*args, **kwargs)

    return wrapper


@bp.route("/login", methods=["GET", "POST"])
@logged_out
def login():
    form = LoginForm()
    if form.validate_on_submit():
        next = request.args.get("next")
        if user := User.authenticate(form.username.data, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(next or url_for("index.home_page"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("auth.login", next=next))
    return render_template("auth/login.html", form=form)


@bp.route("/signin", methods=["GET", "POST"])
@logged_out
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        # Add signin logic here
        if not User.get_user_by_username(form.username.data):
            new_user = User.create(form.username.data, form.password.data)
            login_user(new_user, remember=form.remember_me.data)
            return redirect(url_for("index.home_page"))
        else:
            flash("Username already exists")
            return redirect(url_for("auth.signin"))
    return render_template("auth/signin.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
