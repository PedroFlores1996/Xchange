import pytest
from flask import template_rendered
from flask_login import login_user, logout_user, current_user
from app.model.user import User


@pytest.fixture(scope="function")
def csrf_token(client):
    response = client.get("/login")
    return response.data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]


@pytest.fixture(scope="function")
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture(scope="function")
def login_before(db_session, request_context):
    user = User.create("user1", "password1")
    login_user(user)
    assert current_user.is_authenticated
    yield


@pytest.fixture(scope="function")
def reset_login(request_context):
    assert not current_user.is_authenticated
    yield
    logout_user()
    assert not current_user.is_authenticated
