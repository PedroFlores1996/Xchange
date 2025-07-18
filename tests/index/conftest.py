import pytest
from flask import template_rendered
from flask_login import login_user, logout_user, current_user
from app.model.user import User


@pytest.fixture(scope="function")
def captured_templates(app):
    """Fixture to capture templates rendered during tests."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture(scope="function")
def authenticated_user(db_session, request_context):
    """Fixture that creates and logs in a user."""
    user = User.create("testuser", "test@example.com", "password123")
    login_user(user)
    assert current_user.is_authenticated
    yield user
    logout_user()


@pytest.fixture(scope="function")
def unauthenticated_user(request_context):
    """Fixture that ensures no user is logged in."""
    logout_user()
    assert not current_user.is_authenticated
    yield
    logout_user()