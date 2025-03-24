from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.group import get_group_members

bp = Blueprint("groups", __name__)


@bp.route("/groups/<int:group_id>/users", methods=["GET"])
@login_required
def get_group_users(group_id):
    if group_members := get_group_members(current_user, group_id):
        return jsonify(
            [{"id": user.id, "username": user.username} for user in group_members]
        )
    else:
        return jsonify({"error": "Group not found or access denied"}), 404
