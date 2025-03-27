from app.model.user import User


def get_user_group(user: User, group_id: int) -> list[User] | None:
    """
    Finds the user's group that matches the group_id and returns all members in it.

    :param user: The user object
    :param group_id: The ID of the group to search for
    :return: The list of members in the group, or None if the group is not found
    """
    return next((g for g in user.groups if g.id == group_id), None)
