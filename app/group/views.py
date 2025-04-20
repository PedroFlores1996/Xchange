from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user

from app.group import get_authorized_group
from app.debt import get_group_user_debts

bp = Blueprint("groups", __name__)


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
        user_debts = get_group_user_debts(group.users, group.id)
        return render_template("group/debts.html", group=group, user_debts=user_debts)

    else:
        return jsonify({"error": "Group not found or access denied"}), 404
