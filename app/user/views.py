from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.model.user import User
from app.user.forms import AddFriendForm
from app.debt import get_debts_total_balance
from app.model.constants import NO_GROUP

bp = Blueprint("user", __name__)


@bp.route("/user/debts", methods=["GET"])
@login_required
def user_debts():
    debts = current_user.lender_debts + current_user.borrower_debts
    balance = get_debts_total_balance(
        current_user.lender_debts, current_user.borrower_debts
    )
    return render_template("user/debts.html", debts=debts, balance=balance)


@bp.route("/user/groups", methods=["GET"])
@login_required
def user_groups():
    groups = current_user.groups
    return render_template("user/groups.html", groups=groups)


@bp.route("/user/friends", methods=["GET", "POST"])
@login_required
def friends():
    form = AddFriendForm()
    if form.validate_on_submit():
        email = form.email.data
        if friend := User.get_user_by_email(email):
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


@bp.route("/user/expenses", methods=["GET"])
@login_required
def expenses():
    expenses = current_user.expenses
    return render_template("user/expenses.html", expenses=expenses)


@bp.route("/user/balances", methods=["GET"])
@login_required
def balance():
    group_balances = dict.fromkeys([group.id for group in current_user.groups], 0)
    group_balances[NO_GROUP] = 0
    overall_balance = 0
    for debt in current_user.lender_debts:
        group_balances[debt.group_id] += debt.amount
        overall_balance += debt.amount
    for debt in current_user.borrower_debts:
        group_balances[debt.group_id] -= debt.amount
        overall_balance -= debt.amount
    return render_template(
        "user/balances.html",
        group_balances=group_balances,
        overall_balance=overall_balance,
    )
