from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.group import get_no_group_debts, get_no_group_user_balances
from app.model.user import User
from app.user import get_user_balances
from app.user.forms import AddFriendForm
from app.debt import get_debts_total_balance
from app.model.constants import NO_GROUP
from app.expense import ExpenseData
from app.model.expense import ExpenseCategory
from app.expense.submit import submit_expense
from app.split import SplitType
from app.database import db

bp = Blueprint("user", __name__)


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


@bp.route("/user/debts", methods=["GET"])
@login_required
def debts():
    debts = current_user.lender_debts + current_user.borrower_debts
    balance = get_debts_total_balance(
        current_user.lender_debts, current_user.borrower_debts
    )
    return render_template("user/debts.html", debts=debts, balance=balance)


@bp.route("/user/groups", methods=["GET"])
@login_required
def groups():
    group_balances, overall_balance = get_user_balances(current_user)
    groups_sorted = sorted(
        [group for group in current_user.groups if group.id != NO_GROUP],
        key=lambda group: group_balances[group.id],
        reverse=True,
    )
    no_group_balance = group_balances.pop(NO_GROUP)
    overall_group_balance = overall_balance - no_group_balance
    return render_template(
        "user/groups.html",
        current_user=current_user,
        groups=groups_sorted,
        group_balances=group_balances,
        overall_balance=overall_group_balance,
    )


@bp.route("/user/friends", methods=["GET", "POST"])
@login_required
def friends():
    form = AddFriendForm()
    if form.validate_on_submit():
        email = form.email.data
        if friend := User.get_user_by_email(email):
            if friend in current_user.friends:
                flash(
                    f"User {friend.username} with email {email} is already your friend",
                    "info",
                )
                return redirect(url_for("user.add_friend_form"))
            else:
                current_user.add_friends(friend)
                flash(
                    f"User {friend.username} with email {email} added as a friend",
                    "success",
                )
        else:
            flash(f"No user found with email {email}", "danger")
            return redirect(url_for("user.add_friend_form"))

        return redirect(url_for("user.friends"))

    friends_debts = get_no_group_user_balances(current_user)
    friends = sorted(
        current_user.friends,
        key=lambda friend: abs(friends_debts.get(friend.id, 0)),
        reverse=True,
    )
    return render_template("user/friends.html", friends=friends, debts=friends_debts)


@bp.route("/user/friend-form", methods=["GET"])
@login_required
def add_friend_form():
    form = AddFriendForm()
    return render_template("user/add_friend_form.html", form=form)


@bp.route("/user/expenses", methods=["GET"])
@login_required
def expenses():
    expenses = current_user.expenses
    return render_template(
        "user/expenses.html", current_user=current_user, expenses=expenses
    )


@bp.route("/user/balances", methods=["GET"])
@login_required
def balance():
    group_balances, overall_balance = get_user_balances(current_user)

    # Sort group_balances by absolute balance amount in descending order
    sorted_group_balances = dict(
        sorted(group_balances.items(), key=lambda item: abs(item[1]), reverse=True)
    )

    return render_template(
        "user/balances.html",
        groups=current_user.groups,
        group_balances=sorted_group_balances,
        overall_balance=overall_balance,
    )


@bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def user_profile(user_id):
    # Check if the user_id corresponds to the current_user's ID
    if user_id == current_user.id:
        return redirect(url_for("user.user_dashboard"))

    # Check if the user_id belongs to one of the current_user's friends
    friend = next(
        (friend for friend in current_user.friends if friend.id == user_id), None
    )
    if friend:
        # Get all debts between the current_user and the friend
        debt_with_friend = next(
            (
                debt
                for debt in current_user.lender_debts + current_user.borrower_debts
                if debt.lender_id == friend.id or debt.borrower_id == friend.id
            ),
            None,
        )

        # Get all the current user's expenses involving the friend
        expenses_with_friend = [
            expense
            for expense in current_user.expenses
            if friend in [balance.user for balance in expense.balances]
        ]

        # Get common groups between current user and friend
        current_user_groups = set(current_user.groups)
        friend_groups = set(friend.groups)
        common_groups = list(current_user_groups.intersection(friend_groups))

        # Sort common groups by name
        common_groups.sort(key=lambda group: group.name)

        # Render a profile page for the friend
        return render_template(
            "user/friend.html",
            friend=friend,
            debt=debt_with_friend,
            expenses=expenses_with_friend,
            common_groups=common_groups,
        )

    # If not the current_user or a friend, return 403 Forbidden
    return jsonify({"error": "User not found, or not added as a friend"}), 403


@bp.route("/users/<int:friend_id>/settle", methods=["GET"])
@login_required
def settle_friend_form(friend_id):
    """Show settlement preview for friend debt"""
    # Check if friend exists and is actually a friend
    friend = next(
        (friend for friend in current_user.friends if friend.id == friend_id), None
    )
    if not friend:
        flash("Friend not found", "error")
        return redirect(url_for("user.friends"))

    # Get debt between current user and friend
    debt_with_friend = next(
        (
            debt
            for debt in current_user.lender_debts + current_user.borrower_debts
            if debt.lender_id == friend.id or debt.borrower_id == friend.id
        ),
        None,
    )

    # Calculate debt amount from current user's perspective
    if debt_with_friend:
        if debt_with_friend.lender_id == current_user.id:
            # Current user is owed money (positive)
            debt_amount = debt_with_friend.amount
        else:
            # Current user owes money (negative)
            debt_amount = -debt_with_friend.amount
    else:
        debt_amount = 0

    return render_template(
        "user/settle_friend.html", friend=friend, debt_amount=debt_amount
    )


@bp.route("/users/<int:friend_id>/settle", methods=["POST"])
@login_required
def settle_friend_debt(friend_id):
    """Process settlement between current user and friend"""
    # Check if friend exists and is actually a friend
    friend = next(
        (friend for friend in current_user.friends if friend.id == friend_id), None
    )
    if not friend:
        flash("Friend not found", "error")
        return redirect(url_for("user.friends"))

    # Get debt between current user and friend
    debt_with_friend = next(
        (
            debt
            for debt in current_user.lender_debts + current_user.borrower_debts
            if debt.lender_id == friend.id or debt.borrower_id == friend.id
        ),
        None,
    )

    if not debt_with_friend:
        flash("No debt found between you and this friend", "info")
        return redirect(url_for("user.user_profile", user_id=friend_id))

    # Calculate settlement details
    if debt_with_friend.lender_id == current_user.id:
        # Current user is owed money - friend pays current user
        payer = friend
        receiver = current_user
        amount = debt_with_friend.amount
    else:
        # Current user owes money - current user pays friend
        payer = current_user
        receiver = friend
        amount = debt_with_friend.amount

    # Create settlement expense
    settlement_description = (
        f"Debt settlement between {payer.username} and {receiver.username}"
    )

    print(
        f"DEBUG: About to settle debt - payer: {payer.username}, receiver: {receiver.username}, amount: {amount}"
    )
    print(f"DEBUG: Current user: {current_user.username}")

    try:
        expense_data = ExpenseData(
            creator_id=current_user.id,
            group_id=None,  # Individual settlement, no group
            description=settlement_description,
            amount=amount,
            category=ExpenseCategory.SETTLEMENT,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            payers={payer.id: amount},  # Payer pays the full amount
            owers={receiver.id: amount},  # Receiver is owed the full amount
        )

        print(f"DEBUG: Created expense_data: {expense_data}")

        expense = submit_expense(expense_data)
        print(f"DEBUG: Created expense: {expense.id if expense else 'None'}")

        flash(
            f"Successfully settled debt with {friend.username} for {amount:.2f}",
            "success",
        )

    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback

        traceback.print_exc()
        db.session.rollback()
        flash(f"Error settling debt: {str(e)}", "error")

    return redirect(url_for("user.user_profile", user_id=friend_id))
