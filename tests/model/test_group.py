import pytest
from app.model.group import Group
from app.model.user import User


def test_create_new_group(db_session):
    """Simply creates a new group."""
    Group.create("group1")

    assert Group.query.count() == 1
    assert Group.query.first().name == "group1"


def test_create_duplicate_group(db_session):
    """Create a group with a duplicate name.
    Allowed.
    """
    Group.create("group1")
    Group.create("group1")

    assert Group.query.count() == 2


def test_update_group_description(db_session):
    """Updates the description of a group."""
    group = Group.create("group1")

    assert group.description is None

    group.update_description("new description")

    assert group.description == "new description"
    assert Group.query.first().description == "new description"


def test_add_user(db_session):
    """Adds a user to a group."""
    group = Group.create("group1")
    user = User.create("user1", "password")

    group.add_user(user)

    ## Check group object
    assert len(group.users) == 1
    assert user in group.users

    ## Check group database entry
    db_group = Group.query.filter_by(name="group1").first()
    assert len(db_group.users) == 1
    assert user in db_group.users

    ## Check user object
    assert len(user.groups) == 1
    assert group in user.groups

    ## Check user database entry
    db_user = User.query.filter_by(username="user1").first()
    assert len(db_user.groups) == 1
    assert group in db_user.groups


def test_add_user_is_idempotent(db_session):
    """Adding user to a group is idempotent."""
    group = Group.create("group1")
    user = User.create("user1", "password")

    group.add_user(user)
    group.add_user(user)

    assert len(group.users) == 1
    assert len(user.groups) == 1
    assert len(Group.query.filter_by(name="group1").first().users) == 1


def test_add_multiple_users(db_session):
    """Adding multiple users to a group."""
    group = Group.create("group1")
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")

    group.add_user(user1)
    group.add_user(user2)

    assert len(group.users) == 2
    assert len(user1.groups) == 1
    assert len(user2.groups) == 1
    assert len(Group.query.filter_by(name="group1").first().users) == 2


def test_remove_last_user(db_session):
    """Removes last user from a group and deletes group."""
    group = Group.create("group1")
    user = User.create("user1", "password")

    group.add_user(user)
    group.remove_user(user)

    assert len(group.users) == 0
    assert len(user.groups) == 0
    assert Group.query.count() == 0
    assert User.query.count() == 1


def test_remove_not_last_user(db_session):
    """Removes a user (not the last) from a group."""
    group = Group.create("group1")
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")

    group.add_user(user1)
    group.add_user(user2)
    group.remove_user(user1)

    assert len(group.users) == 1
    assert len(user1.groups) == 0
    assert len(user2.groups) == 1
    assert Group.query.count() == 1
    assert user2 in Group.query.first().users
    assert User.query.count() == 2


def test_remove_user_not_in_group(db_session):
    """Remove a user that is not in the group."""
    group = Group.create("group1")
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")

    group.add_user(user1)
    group.remove_user(user2)

    assert len(group.users) == 1
    assert len(user1.groups) == 1
    assert len(user2.groups) == 0
    assert Group.query.count() == 1
    assert User.query.count() == 2
