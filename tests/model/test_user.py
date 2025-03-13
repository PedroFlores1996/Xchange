import pytest
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from app.model.user import User
from app.model.group import Group


def test_create_new_user(db_session):
    """Simply creates a new user."""
    User.create("user1", "password")

    assert User.query.count() == 1
    assert User.query.first().username == "user1"


def test_create_duplicate_user(db_session):
    """Tries to create a user with a duplicate username.
    Unique constrain on username enforced.
    """
    User.create("user1", "password")

    with pytest.raises(IntegrityError):
        User.create("user1", "password")


def test_create_user_hashes_password(db_session):
    """Creates a new user and hashes the password."""
    User.create("user1", "password")
    user = User.query.first()

    assert user.password != "password"
    assert check_password_hash(user.password, "password")


def test_authenticate_user(db_session):
    """Creates a new user and authenticates it."""
    User.create("user1", "password")

    user = User.authenticate("user1", "password")

    assert user.username == "user1"
    assert User.authenticate("user1", "wrong_password") is None


def test_get_user_by_username(db_session):
    """Creates a new user and retrieves it by username."""
    User.create("user1", "password")

    user = User.get_user_by_username("user1")
    non_existent_user = User.get_user_by_username("non_existent_user")

    assert user is not None
    assert user.username == "user1"
    assert non_existent_user is None


def test_add_to_group(db_session, group_creator):
    """Creates a new user and adds it to a group."""
    user = User.create("user1", "password")
    group = Group.create("group1", [group_creator])

    user.add_to_group(group)

    # Check objects
    assert user.groups == [group]
    assert group.users == [group_creator, user]

    # Check database entries
    assert User.query.filter_by(username="user1").first().groups == [group]
    assert Group.query.filter_by(name="group1").first().users == [group_creator, user]


def test_add_to_same_group(db_session, group_creator):
    """Adding a user to a group is idempotent."""
    user = User.create("user1", "password")
    group = Group.create("group1", [group_creator])

    user.add_to_group(group)
    user.add_to_group(group)

    assert user.groups == [group]
    assert group.users == [group_creator, user]
    assert User.query.count() == 2
    assert Group.query.count() == 1


def test_add_to_multiple_groups(db_session, group_creator):
    """Adding a user to multiple groups."""
    user = User.create("user1", "password")
    group1 = Group.create("group1", [group_creator])
    group2 = Group.create("group2", [group_creator])

    user.add_to_group(group1)
    user.add_to_group(group2)

    assert user.groups == [group1, group2]
    assert group1.users == [group_creator, user]
    assert group2.users == [group_creator, user]
    assert User.query.count() == 2
    assert Group.query.count() == 2


def test_add_multiple_users_to_group(db_session, group_creator):
    """Adding multiple users to a group."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    group = Group.create("group1", [group_creator])

    user1.add_to_group(group)
    user2.add_to_group(group)

    assert user1.groups == [group]
    assert user2.groups == [group]
    assert group.users == [group_creator, user1, user2]
    assert User.query.count() == 3
    assert Group.query.count() == 1


def test_remove_from_group_last_user(db_session, group_creator):
    """Creates a new user and removes it from a group."""
    group = Group.create("group1", [group_creator])

    group_creator.remove_from_group(group)

    assert group not in group_creator.groups
    assert group_creator not in group.users
    assert User.query.count() == 1
    assert Group.query.count() == 0


def test_remove_from_group_last_user_idempotent(db_session, group_creator):
    """Creates a new user and removes it from a group."""
    group = Group.create("group1", [group_creator])

    group_creator.remove_from_group(group)
    group_creator.remove_from_group(group)

    assert group_creator not in group.users
    assert group not in group_creator.groups
    assert User.query.count() == 1
    assert Group.query.count() == 0


def test_remove_from_group_not_last_user(db_session, group_creator):
    """Creates a new user and removes it from a group."""
    user = User.create("user", "password")
    group = Group.create("group1", [group_creator])

    user.add_to_group(group)
    group_creator.remove_from_group(group)

    assert group not in group_creator.groups
    assert group_creator not in group.users
    assert user in group.users
    assert group in user.groups
    assert User.query.count() == 2
    assert Group.query.count() == 1


def test_remove_from_group_not_last_user_idempotent(db_session, group_creator):
    """Creates a new user and removes it from a group."""
    user = User.create("user1", "password")
    group = Group.create("group1", [group_creator])

    user.add_to_group(group)
    user.remove_from_group(group)
    user.remove_from_group(group)

    assert group not in user.groups
    assert user not in group.users
    assert User.query.count() == 2
    assert Group.query.count() == 1


def test_add_friends(db_session):
    """Creates a new user and adds friends."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    user3 = User.create("user3", "password")

    user1.add_friends(user2, user3)

    assert User.query.count() == 3
    assert user1.friends == [user2, user3]
    assert user2.friends == [user1]
    assert user3.friends == [user1]


def test_add_same_friend_idempotent(db_session):
    """Adding a friend is idempotent."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")

    user1.add_friends(user2)
    user1.add_friends(user2)

    assert user1.friends == [user2]
    assert user2.friends == [user1]
    assert User.query.count() == 2


def test_add_multiple_friends(db_session):
    """Adding multiple friends."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    user3 = User.create("user3", "password")

    user1.add_friends(user2, user3)

    assert user1.friends == [user2, user3]
    assert user2.friends == [user1]
    assert user3.friends == [user1]
    assert User.query.count() == 3


def test_remove_friends(db_session):
    """Creates a new user and removes friends."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    user3 = User.create("user3", "password")

    user1.add_friends(user2, user3)
    user1.remove_friends(user2, user3)

    assert User.query.count() == 3
    assert user1.friends == []
    assert user2.friends == []
    assert user3.friends == []


def test_remove_same_friend_idempotent(db_session):
    """Removing a friend is idempotent."""
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")

    user1.add_friends(user2)
    user1.remove_friends(user2)
    user1.remove_friends(user2)

    assert user1.friends == []
    assert user2.friends == []
    assert User.query.count() == 2
