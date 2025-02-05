import pytest
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from app.model.user import User
from app.model.group import Group


def test_create_new_user(db_session):
    """Simply creates a new user."""
    User.create_user("user1", "password")

    assert User.query.count() == 1
    assert User.query.first().username == "user1"


def test_create_duplicate_user(db_session):
    """Tries to create a user with a duplicate username.
    Unique constrain on username enforced.
    """
    User.create_user("user1", "password")

    with pytest.raises(IntegrityError):
        User.create_user("user1", "password")


def test_create_user_hashes_password(db_session):
    """Creates a new user and hashes the password."""
    User.create_user("user1", "password")
    user = User.query.first()

    assert user.password != "password"
    assert check_password_hash(user.password, "password")


def test_authenticate_user(db_session):
    """Creates a new user and authenticates it."""
    User.create_user("user1", "password")

    user = User.authenticate("user1", "password")

    assert user.username == "user1"
    assert User.authenticate("user1", "wrong_password") is False


def test_get_user_by_username(db_session):
    """Creates a new user and retrieves it by username."""
    User.create_user("user1", "password")

    user = User.get_user_by_username("user1")
    non_existent_user = User.get_user_by_username("non_existent_user")

    assert user is not None
    assert user.username == "user1"
    assert non_existent_user is None


def test_add_to_group(db_session):
    """Creates a new user and adds it to a group."""
    user = User.create_user("user1", "password")
    group = Group.create_group("group1")

    user.add_to_group(group)

    assert group in user.groups
    assert user in group.users
    assert user.groups == [group]
    assert group.users == [user]


def test_add_to_same_group(db_session):
    """Adding a user to a group is idempotent."""
    user = User.create_user("user1", "password")
    group = Group.create_group("group1")

    user.add_to_group(group)
    user.add_to_group(group)

    assert user.groups == [group]
    assert group.users == [user]
    assert User.query.count() == 1
    assert Group.query.count() == 1


def test_add_to_multiple_groups(db_session):
    """Adding a user to multiple groups."""
    user = User.create_user("user1", "password")
    group1 = Group.create_group("group1")
    group2 = Group.create_group("group2")

    user.add_to_group(group1)
    user.add_to_group(group2)

    assert user.groups == [group1, group2]
    assert group1.users == [user]
    assert group2.users == [user]
    assert User.query.count() == 1
    assert Group.query.count() == 2


def test_add_multiple_users_to_group(db_session):
    """Adding multiple users to a group."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")
    group = Group.create_group("group1")

    user1.add_to_group(group)
    user2.add_to_group(group)

    assert user1.groups == [group]
    assert user2.groups == [group]
    assert group.users == [user1, user2]
    assert User.query.count() == 2
    assert Group.query.count() == 1
