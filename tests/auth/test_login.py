import pytest
from flask import template_rendered, url_for
from flask_login import login_user, logout_user, current_user
from app.auth import load_user
from app.auth.forms import LoginForm
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


def test_load_user(db_session):
    user = User.create("testuser", "password")

    loaded_user = load_user(user.id)

    assert loaded_user is not None
    assert loaded_user.id == user.id


def test_load_user_inexistent_user(db_session):
    loaded_user = load_user(1)

    assert loaded_user is None


def test_logout_authenticated_user(client, login_before):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated


def test_logout_no_authenticated_user(client, reset_login):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated


def test_login_get(client, captured_templates):
    response = client.get("/login")

    assert response.status_code == 200
    assert len(captured_templates) == 1
    assert captured_templates[0][0].name == "auth/login.html"
    assert isinstance(captured_templates[0][1]["form"], LoginForm)


def test_login_post(db_session, client, reset_login, csrf_token):
    User.create("user1", "password1")

    response = client.post(
        "/login",
        data={"username": "user1", "password": "password1", "csrf_token": csrf_token},
    )

    assert current_user.is_authenticated
    assert response.status_code == 302
    assert response.location == url_for("index.home_page")


def test_login_post_inexistent_user(db_session, client, reset_login, csrf_token):
    response = client.post(
        "/login",
        data={"username": "user1", "password": "password1", "csrf_token": csrf_token},
    )

    assert User.query.count() == 0
    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated


def test_login_post_invalid_password(db_session, client, reset_login, csrf_token):
    User.create("user1", "password1")

    response = client.post(
        "/login",
        data={"username": "user1", "password": "invalid_password", "csrf_token": csrf_token},
    )

    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated
