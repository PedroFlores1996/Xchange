from app.model.user import User
from app.auth import load_user


def test_load_user(db_session):
    user = User.create("testuser", "password")

    loaded_user = load_user(user.id)

    assert loaded_user is not None
    assert loaded_user.id == user.id


def test_load_user_inexistent_user(db_session):
    loaded_user = load_user(1)

    assert loaded_user is None
