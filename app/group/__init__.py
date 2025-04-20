from flask_login import current_user
from app.model.group import Group


def get_authorized_group(group_id: int) -> Group | None:
    """
    Finds the user's group that matches the group_id and returns all members in it.

    :param user: The user object
    :param group_id: The ID of the group to search for
    :return: The list of members in the group, or None if the group is not found
    """
    return next((g for g in current_user.groups if g.id == group_id), None)
