from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug import Response

from app.group import (
    get_authorized_group,
    get_group_user_expenses,
    get_group_user_debts,
    get_group_user_balances,
)
from app.split.constants import OWED, PAYED, TOTAL
from app.group.forms import GroupForm
from app.model.group import Group
from app.model.user import User
from app.expense.forms import ExpenseForm


bp = Blueprint("groups", __name__)


@bp.route("/groups", methods=["POST"])
@login_required
def create_group():
    """
    Creates a new group for the current user using GroupForm.
    Returns a redirect to the group overview or re-renders the form with errors.
    """
    form = GroupForm()

    if form.validate_on_submit():
        # Start with current user
        user_ids = [current_user.id]

        # Add friend IDs if provided
        if form.friend_ids.data:
            friend_ids = [
                int(id.strip()) for id in form.friend_ids.data.split(",") if id.strip()
            ]
            user_ids.extend(friend_ids)

        # Fallback to old users field for backwards compatibility
        if form.users.data:
            old_user_ids = [id for id in form.users.data if id]
            user_ids.extend(old_user_ids)

        # Remove duplicates just in case
        user_ids = list(set(user_ids))

        # Query User objects
        users = User.query.filter(User.id.in_(user_ids)).all()

        # Create group using the model's create method
        group = Group.create(
            name=form.name.data,
            users=users,
            description=form.description.data,
        )
        flash("Group created successfully!", "success")
        return redirect(url_for("groups.get_group_overview", group_id=group.id))
    else:
        # If not valid, re-render the form with errors
        return render_template("group/create_group.html", form=form), 400


@bp.route("/groups/create_group_form", methods=["GET"])
@login_required
def create_group_form():
    """
    Renders the form to create a new group.
    """
    form = GroupForm()
    # Convert friends to JSON-serializable format
    friends_data = [
        {"id": friend.id, "username": friend.username}
        for friend in current_user.friends
    ]
    return render_template(
        "group/create_group_form.html", form=form, friends_data=friends_data
    )


@bp.route("/groups/<int:group_id>", methods=["GET"])
@login_required
def get_group_overview(group_id):
    """
    Displays the current user's total balance, debts, and recent expenses in the group.
    """
    if group := get_authorized_group(group_id):
        # Get the current user's total balance in the group

        group_user_debts = get_group_user_debts(group)

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted by absolute value descending, and filter out zeros
        group_user_balances = get_group_user_balances(group)

        # Get the current user's debts in the group
        current_user_debts = group_user_debts.get(
            current_user.id, {OWED: [], PAYED: [], TOTAL: 0.0}
        )
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
def group_expenses(group_id):
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

        # Get group balances for all users in the group
        group_balances = get_group_user_balances(group)

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted from most negative to most positive
        balances_by_amount = dict(
            sorted(
                group_balances.items(),
                key=lambda item: item[1],
            )
        )

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted from most positive to most negative
        balances_by_amount_reversed = dict(reversed(balances_by_amount.items()))

        # Get all users balances in the group as a dictionary {User: total_balance}, sorted by absolute value descending
        balances_by_abs_amount = dict(
            sorted(
                group_balances.items(),
                key=lambda item: abs(item[1]),
                reverse=True,
            )
        )

        return render_template(
            "group/balances.html",
            group=group,
            balances_abs=balances_by_abs_amount,
            balances=balances_by_amount,
            balances_reversed=balances_by_amount_reversed,
        )
    else:

        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/new-expense", methods=["GET"])
@login_required
def new_group_expense(group_id) -> str | Response:
    """
    Creates a new expense for a specific group.
    Pre-fills the group field and filters users to group members.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    form = ExpenseForm()
    return render_template(
        "expense/expense.html",
        form=form,
        current_user=current_user,
        group=group,
        pre_selected_group_id=group_id,
    )
