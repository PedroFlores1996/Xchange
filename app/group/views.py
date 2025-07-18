from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug import Response

from app.group import (
    get_authorized_group,
    get_group_user_expenses,
    get_group_user_debts,
    get_group_user_balances,
    check_group_has_balances,
    calculate_group_settlement_transactions,
    handle_settle_debts_process,
    handle_individual_balance_confirmation,
    handle_individual_balance_process,
)
from app.split.constants import OWED, PAYED, TOTAL
from app.group.forms import GroupForm, AddUserToGroupForm
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


@bp.route("/groups/<int:group_id>/users", methods=["GET", "POST"])
@login_required
def get_group_users(group_id):
    """
    Shows all users in a group with the ability to add new users.
    Displays existing group members and form to add new ones.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    form = AddUserToGroupForm()

    if form.validate_on_submit():
        if form.friend_ids.data:
            friend_ids = [
                int(id.strip()) for id in form.friend_ids.data.split(",") if id.strip()
            ]

            # Get users who are not already in the group
            users_to_add = User.query.filter(
                User.id.in_(friend_ids), ~User.id.in_([user.id for user in group.users])
            ).all()

            if users_to_add:
                group.add_users(users_to_add)
                usernames = [user.username for user in users_to_add]
                flash(
                    f"Successfully added {', '.join(usernames)} to {group.name}!",
                    "success",
                )
            else:
                flash(
                    "No new users to add or all selected users are already in the group.",
                    "warning",
                )
        else:
            flash("Please select at least one user to add.", "warning")

        return redirect(url_for("groups.get_group_users", group_id=group_id))

    # Get available users (friends who are not already in the group)
    available_friends = [
        friend for friend in current_user.friends if friend not in group.users
    ]

    friends_data = [
        {"id": friend.id, "username": friend.username} for friend in available_friends
    ]

    return render_template(
        "group/users_with_add.html",
        form=form,
        group=group,
        friends_data=friends_data,
    )


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


@bp.route("/groups/<int:group_id>/settle", methods=["GET"])
@login_required
def settle_debts_preview(group_id) -> str | Response:
    """
    Shows a preview of settlement transactions that will be created to settle all debts in the group.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    # Check if there are any non-zero balances to settle
    if not check_group_has_balances(group):
        flash("No Active Debts to Settle", "info")
        return redirect(url_for("groups.get_group_overview", group_id=group_id))

    # Calculate settlement transactions
    settlement_transactions = calculate_group_settlement_transactions(group)

    return render_template(
        "group/settle_preview.html",
        group=group,
        settlement_transactions=settlement_transactions,
        current_user=current_user,
    )


@bp.route("/groups/<int:group_id>/settle", methods=["POST"])
@login_required
def settle_debts_process(group_id) -> str | Response:
    """
    Processes the settlement by creating settlement expenses for all transactions.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    result = handle_settle_debts_process(group)
    
    if not result['success']:
        flash(result['message'], result['message_type'])
        return redirect(url_for("groups.get_group_overview", group_id=group_id))

    flash(result['message'], result['message_type'])
    return render_template(
        "group/settle_success.html",
        group=group,
        settlement_expenses=result['settlement_expenses'],
        current_user=current_user,
    )


@bp.route("/groups/<int:group_id>/settle/<int:user_id>", methods=["GET"])
@login_required
def settle_individual_balance_confirmation(group_id, user_id) -> str | Response:
    """
    Shows confirmation page for settling an individual user's balance within a group.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    result = handle_individual_balance_confirmation(group, user_id)
    
    if not result['success']:
        flash(result['message'], result['message_type'])
        return redirect(url_for("groups.get_group_debts", group_id=group_id))
    
    return render_template(
        "group/settle_individual_confirmation.html",
        group=group,
        user=result['user'],
        user_balance=result['user_balance'],
        settlement_transactions=result['settlement_transactions'],
        current_user=current_user,
    )


@bp.route("/groups/<int:group_id>/settle/<int:user_id>", methods=["POST"])
@login_required
def settle_individual_balance_process(group_id, user_id) -> str | Response:
    """
    Processes the settlement of an individual user's balance within a group.
    """
    group = get_authorized_group(group_id)
    if not group:
        flash("Group not found or access denied.", "danger")
        return redirect(url_for("user.user_dashboard"))

    result = handle_individual_balance_process(group, user_id)
    
    if not result['success']:
        flash(result['message'], result['message_type'])
        return redirect(url_for("groups.get_group_debts", group_id=group_id))
    
    return render_template(
        "group/settle_individual_success.html",
        group=group,
        user=result['user'],
        settlement_expenses=result['settlement_expenses'],
        current_user=current_user,
    )
