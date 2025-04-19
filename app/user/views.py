from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.model.user import User
from app.user import get_user_balances
from app.user.forms import AddFriendForm
from app.debt import get_debts_total_balance, get_no_group_debts
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
    group_balances, overall_balance = get_user_balances(current_user)
    return render_template(
        "user/balances.html",
        group_balances=group_balances,
        overall_balance=overall_balance,
    )


@bp.route("/user", methods=["GET"])
@login_required
def user_dashboard():
    # 1st Column: Debts outside any group
    no_group_debts = get_no_group_debts(current_user)
    no_group_debts = sorted(
        no_group_debts, key=lambda debt: abs(debt.amount), reverse=True
    )

    # 2nd Column: Groups ordered by balance or name
    group_balances, overall_balance = get_user_balances(current_user)
    groups_sorted = sorted(
        [group for group in current_user.groups if group.id != NO_GROUP],
        key=lambda group: group_balances[group.id],
        reverse=True,
    )
    no_group_balance = group_balances.pop(NO_GROUP)
    overall_group_balance = overall_balance - no_group_balance

    return render_template(
        "user/dashboard.html",
        current_user=current_user,
        no_group_debts=no_group_debts,
        no_group_balance=no_group_balance,
        groups=groups_sorted,
        group_balances=group_balances,
        overall_group_balance=overall_group_balance,
        expenses=current_user.expenses,
    )
