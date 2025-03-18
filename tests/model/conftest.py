import pytest
from app.model.user import User


@pytest.fixture
def group_creator(db_session):
    return User.create("group_creator", "group_creator@email.com", "password")
