import pytest
from flask_login import login_user, logout_user
from app.group import get_authorized_group
from app.model.user import User
from app.model.group import Group


@pytest.fixture
def logged_in_user(db_session):
    # Create and log in user1
    user = User.create("user1", "email1", "password")
    login_user(user)  # Log in the user
    yield user  # Yield the logged-in user for the test
    logout_user()


def test_get_user_group(request_context, logged_in_user):
    group = Group.create("group_name", [logged_in_user])

    assert get_authorized_group(group.id) == group


def test_get_user_group_not_found(request_context, logged_in_user):
    other_user = User.create("user2", "email2", "password")
    group = Group.create("group_name", [other_user])

    assert get_authorized_group(group.id) is None
