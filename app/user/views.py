from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.model.user import User

bp = Blueprint("user", __name__)


@bp.route("/users/debts", methods=["GET"])
@login_required
def user_debts():
    debts = current_user.lender_debts + current_user.borrower_debts
    return render_template("user/debts.html", debts=debts)


@bp.route("/users/groups", methods=["GET"])
@login_required
def user_groups():
    groups = current_user.groups
    return render_template("user/groups.html", groups=groups)


@bp.route("/users/friends", methods=["GET", "POST"])
@login_required
def friends():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Username is required.", "warning")
            return redirect(url_for("user.friends"))

        friend = User.query.filter_by(username=username).first()
        if friend:
            current_user.add_friends(friend)
            flash(f"User {username} added as a friend.", "success")
        else:
            flash(f"User {username} does not exist.", "danger")

        return redirect(url_for("user.friends"))

    friends = current_user.friends
    return render_template("user/friends.html", friends=friends)
