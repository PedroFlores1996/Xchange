from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user

from app.group import get_user_group_by_id

bp = Blueprint("groups", __name__)


@bp.route("/groups/<int:group_id>/users", methods=["GET"])
@login_required
def get_group_users(group_id):
    """
    Retrieves the users for a specific group.
    Returns HTML or JSON based on the Accept header.
    """
    if group := get_user_group_by_id(current_user, group_id):
        users = [{"id": user.id, "username": user.username} for user in group.users]

        # Check the Accept header
        if request.accept_mimetypes["text/html"]:
            return render_template("group/users.html", group=group, users=users)
        elif request.accept_mimetypes["application/json"]:
            return jsonify(users)
        else:
            return jsonify({"error": "Unsupported content type"}), 406
    else:
        return jsonify({"error": "Group not found or access denied"}), 404


@bp.route("/groups/<int:group_id>/expenses", methods=["GET"])
@login_required
def get_group_expenses(group_id):
    """
    Retrieves the expenses for a specific group.
    Returns HTML or JSON based on the Accept header.
    """
    if group := get_user_group_by_id(current_user, group_id):
        expenses = [
            {
                "id": expense.id,
                "description": expense.description,
                "amount": expense.amount,
                "category": expense.category,
                "date": expense.date.strftime("%Y-%m-%d"),
            }
            for expense in group.expenses
        ]

        # Check the Accept header
        if request.accept_mimetypes["text/html"]:
            return render_template(
                "group/expenses.html", group=group, expenses=expenses
            )
        elif request.accept_mimetypes["application/json"]:
            return jsonify(expenses)
        else:
            return jsonify({"error": "Unsupported content type"}), 406
    else:
        return jsonify({"error": "Group not found or access denied"}), 404
