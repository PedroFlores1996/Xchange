from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.model.user import User
from app.user.forms import AddFriendForm

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
    form = AddFriendForm()
    if form.validate_on_submit():
        email = form.email.data
        friend = User.query.filter_by(email=email).first()
        if friend:
            if friend in current_user.friends:
                flash(
                    f"User {friend.username} with email {email} is already your friend.",
                    "info",
                )
            else:
                current_user.add_friends(friend)
                flash(
                    f"User {friend.username} with email {email} added as a friend.",
                    "success",
                )
        else:
            flash(f"No user found with email {email}.", "danger")

        return redirect(url_for("user.friends"))

    friends = current_user.friends
    return render_template("user/friends.html", friends=friends)
