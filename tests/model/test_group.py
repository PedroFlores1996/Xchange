import pytest
from app.model.group import Group
from app.model.user import User


def test_create_new_group(db_session, group_creator):
    """Simply creates a new group."""
    group = Group.create("group_name", [group_creator])

    assert Group.query.count() == 1
    assert Group.query.first().name == "group_name"
    assert Group.query.first().users == [group_creator]
    assert Group.query.first() == group


def test_create_group_with_multiple_users(db_session):
    """Creates a group with multiple users."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    group = Group.create("group_name", [user1, user2])

    assert group.users == [user1, user2]


def test_create_group_with_no_users(db_session, group_creator):

    with pytest.raises(ValueError):
        Group.create("group_name", [])


def test_create_duplicate_group(db_session, group_creator):
    """Create a group with a duplicate name.
    Allowed.
    """
    group1 = Group.create("group_name", [group_creator])
    group2 = Group.create("group_name", [group_creator])

    assert group1 is not group2
    assert group1.name == group2.name
    assert Group.query.count() == 2
    assert group_creator.groups == [group1, group2]


def test_update_group_description(db_session, group_creator):
    """Updates the description of a group."""
    group = Group.create("group_name", [group_creator])

    assert group.description is None

    group.update_description("new description")

    assert group.description == "new description"
    assert Group.query.first().description == "new description"


def test_add_user(db_session, group_creator):
    """Adds a user to a group."""
    group = Group.create("group_name", [group_creator])
    user = User.create("username", "email", "password")

    group.add_user(user)

    ## Check group object
    assert len(group.users) == 2
    assert user in group.users

    ## Check group database entry
    db_group = Group.query.filter_by(name="group_name").first()
    assert len(db_group.users) == 2
    assert user in db_group.users

    ## Check user object
    assert len(user.groups) == 1
    assert group in user.groups

    ## Check user database entry
    db_user = User.query.filter_by(username="username").first()
    assert len(db_user.groups) == 1
    assert group in db_user.groups


def test_add_user_is_idempotent(db_session, group_creator):
    """Adding user to a group is idempotent."""
    group = Group.create("group_name", [group_creator])
    user = User.create("username", "email", "password")

    group.add_user(user)
    group.add_user(user)

    assert len(group.users) == 2
    assert len(user.groups) == 1
    assert len(Group.query.filter_by(name="group_name").first().users) == 2


def test_add_multiple_users(db_session, group_creator):
    """Adding multiple users to a group."""
    group = Group.create("group_name", [group_creator])
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    group.add_users([user1, user2])

    assert len(group.users) == 3
    assert len(user1.groups) == 1
    assert len(user2.groups) == 1
    assert len(Group.query.filter_by(name="group_name").first().users) == 3


def test_remove_last_user(db_session, group_creator):
    """Removes last user from a group and deletes group."""
    group = Group.create("group_name", [group_creator])
    group.remove_user(group_creator)

    assert len(group.users) == 0
    assert len(group_creator.groups) == 0
    assert Group.query.count() == 0
    assert User.query.count() == 1


def test_remove_not_last_user(db_session, group_creator):
    """Removes a user (not the last) from a group."""
    group = Group.create("group_name", [group_creator])
    user = User.create("username", "email", "password")

    group.add_user(user)
    group.remove_user(user)

    assert len(group.users) == 1
    assert len(group_creator.groups) == 1
    assert len(user.groups) == 0
    assert Group.query.count() == 1
    assert group_creator in Group.query.first().users
    assert User.query.count() == 2


def test_remove_user_not_in_group(db_session, group_creator):
    """Remove a user that is not in the group."""
    group = Group.create("group_name", [group_creator])
    user = User.create("username", "email", "password")

    group.remove_user(user)

    assert len(group.users) == 1
    assert len(user.groups) == 0
    assert Group.query.count() == 1
    assert User.query.count() == 2
