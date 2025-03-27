from app.group import get_user_group
from app.model.user import User
from app.model.group import Group


def test_get_user_group(db_session):
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    user3 = User.create("user3", "email3", "password")
    group = Group.create("group_name", [user1, user2, user3])

    assert get_user_group(user1, group.id) == [user1, user2, user3]
