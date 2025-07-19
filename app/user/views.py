from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.user import (
    prepare_dashboard_data,
    handle_add_friend,
    prepare_friends_data,
    prepare_groups_data,
    prepare_balances_data,
    validate_friend_access,
    prepare_user_profile_data,
    validate_friend_for_settlement,
    calculate_friend_debt,
    process_friend_debt_settlement,
)
from app.user.forms import AddFriendForm
from app.debt import get_debts_total_balance

bp = Blueprint("user", __name__)


@bp.route("/user", methods=["GET"])
@login_required
def user_dashboard():
    template_data = prepare_dashboard_data(current_user)
    return render_template("user/dashboard.html", **template_data)


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
    template_data = prepare_groups_data(current_user)
    return render_template("user/groups.html", **template_data)


@bp.route("/user/friends", methods=["GET", "POST"])
@login_required
def friends():
    form = AddFriendForm()
    if form.validate_on_submit():
        email = form.email.data
        result = handle_add_friend(current_user, email)
        flash(result['message'], result['message_type'])
        return redirect(url_for(result['redirect_to']))

    template_data = prepare_friends_data(current_user)
    return render_template("user/friends.html", **template_data)


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
    template_data = prepare_balances_data(current_user)
    return render_template("user/balances.html", **template_data)


@bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def user_profile(user_id):
    validation = validate_friend_access(current_user, user_id)
    
    if not validation['valid']:
        if validation.get('redirect_required'):
            return redirect(url_for(validation['redirect_to']))
        else:
            return jsonify({"error": validation['error']}), validation['status_code']
    
    friend = validation['friend']
    template_data = prepare_user_profile_data(current_user, friend)
    return render_template("user/friend.html", **template_data)


@bp.route("/users/<int:friend_id>/settle", methods=["GET"])
@login_required
def settle_friend_form(friend_id):
    """Show settlement preview for friend debt"""
    validation = validate_friend_for_settlement(current_user, friend_id)
    
    if not validation['valid']:
        flash(validation['message'], validation['message_type'])
        return redirect(url_for(validation['redirect_to']))
    
    friend = validation['friend']
    debt_with_friend, debt_amount = calculate_friend_debt(current_user, friend)
    
    return render_template(
        "user/settle_friend.html", friend=friend, debt_amount=debt_amount
    )


@bp.route("/users/<int:friend_id>/settle", methods=["POST"])
@login_required
def settle_friend_debt(friend_id):
    """Process settlement between current user and friend"""
    validation = validate_friend_for_settlement(current_user, friend_id)
    
    if not validation['valid']:
        flash(validation['message'], validation['message_type'])
        return redirect(url_for(validation['redirect_to']))
    
    friend = validation['friend']
    debt_with_friend, debt_amount = calculate_friend_debt(current_user, friend)
    
    result = process_friend_debt_settlement(current_user, friend, debt_with_friend)
    flash(result['message'], result['message_type'])
    
    return redirect(url_for(result['redirect_to'], user_id=friend_id))
