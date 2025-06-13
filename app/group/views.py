from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user

from app.group import (
    get_authorized_group,
    get_group_user_expenses,
    get_group_user_debts,
)
from app.split.constants import OWED, PAYED, TOTAL


bp = Blueprint("groups", __name__)


@bp.route("/groups/<int:group_id>", methods=["GET"])
@login_required
def get_group_overview(group_id):
    """
    Displays the current user's total balance, debts, and recent expenses in the group.
    """
    if group := get_authorized_group(group_id):
        # Get the current user's total balance in the group

        group_user_debts = get_group_user_debts(group)

        # Build a mapping from user_id to User object for quick lookup
        user_id_to_user = {user.id: user for user in group.users}

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted by absolute value descending, and filter out zeros
        group_user_balances = dict(
            sorted(
                (
                    (user_id_to_user[user_id], data[TOTAL])
                    for user_id, data in group_user_debts.items()
                    if data[TOTAL] != 0
                ),
                key=lambda item: abs(item[1]),
                reverse=True,
            )
        )

        # Get the current user's debts in the group
        current_user_debts = group_user_debts[current_user.id]
        user_debts_ordered_by_amount = sorted(
            current_user_debts[OWED] + current_user_debts[PAYED],
            key=lambda x: x.amount,
            reverse=True,
        )

        # Get group expenses sorted by most
        recent_expenses = get_group_user_expenses(current_user, group.id)

        return render_template(
            "group/overview.html",
            group=group,
            balances=group_user_balances,
            user_group_balance=current_user_debts[TOTAL],
            user_group_debts=user_debts_ordered_by_amount,
            recent_expenses=recent_expenses,
        )
    else:
        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/users", methods=["GET"])
@login_required
def get_group_users(group_id):
    """
    Retrieves the users for a specific group.
    Returns HTML or JSON based on the Accept header.
    """
    if group := get_authorized_group(group_id):
        return render_template("group/users.html", group=group)
    else:
        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/expenses", methods=["GET"])
@login_required
def get_group_expenses(group_id):
    """
    Retrieves the expenses for a specific group.
    Returns HTML or JSON based on the Accept header.
    """
    if group := get_authorized_group(group_id):
        return render_template("group/expenses.html", group=group)

    else:
        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/debts", methods=["GET"])
@login_required
def get_group_debts(group_id):
    """
    Retrieves the debts for a specific group.
    Returns HTML or JSON based on the Accept header.
    """
    if group := get_authorized_group(group_id):
        user_debts = get_group_user_debts(group)
        return render_template("group/debts.html", group=group, user_debts=user_debts)

    else:
        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/balances", methods=["GET"])
@login_required
def get_group_balances(group_id):
    """
    Displays the current user's total balance, debts, and recent expenses in the group.
    """
    if group := get_authorized_group(group_id):
        # Get the current user's total balance in the group

        group_user_debts = get_group_user_debts(group)

        # Build a mapping from user_id to User object for quick lookup
        user_id_to_user = {user.id: user for user in group.users}

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted by absolute value descending
        balances_by_abs_amount = dict(
            sorted(
                (
                    (user_id_to_user[user_id], data[TOTAL])
                    for user_id, data in group_user_debts.items()
                ),
                key=lambda item: abs(item[1]),
                reverse=True,
            )
        )

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted from most positive to most negative
        balances_by_amount_reversed = dict(
            sorted(
                balances_by_abs_amount.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted from most negative to most positive
        balances_by_amount = dict(
            sorted(
                balances_by_abs_amount.items(),
                key=lambda item: item[1],
            )
        )

        return render_template(
            "group/balances.html",
            group=group,
            balances_abs=balances_by_abs_amount,
            balances_reversed=balances_by_amount_reversed,
            balances=balances_by_amount,
        )
    else:
        return jsonify({"error": "Group not found or access denied"}), 404
