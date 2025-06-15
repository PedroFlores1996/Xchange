# Create a fixture for a test Expense object
import pytest

from flask_login import login_user, logout_user
from app.model.user import User
from app.model.expense import Expense


@pytest.fixture
def logged_in_user(db_session, request_context):
    user = User.create(
        username="test_user", email="test_user@email.com", password="test_password"
    )
    login_user(user)
    yield user
    logout_user()
