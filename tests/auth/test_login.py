from flask import url_for
from flask_login import current_user  #
from app.auth.forms import LoginForm
from app.model.user import User


def test_login_get(client, captured_templates):
    response = client.get("/login")

    assert response.status_code == 200
    assert len(captured_templates) == 1
    assert captured_templates[0][0].name == "auth/login.html"
    assert isinstance(captured_templates[0][1]["form"], LoginForm)


def test_login_post(db_session, client, reset_login):
    User.create("username", "email", "password")

    response = client.post(
        "/login",
        data={"email": "email", "password": "password"},
    )

    assert current_user.is_authenticated
    assert response.status_code == 302
    assert response.location == url_for("index.home_page")


def test_login_post_inexistent_user(db_session, client, reset_login):
    response = client.post(
        "/login",
        data={"email": "email", "password": "password"},
    )

    assert User.query.count() == 0
    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated


def test_login_post_invalid_password(db_session, client, reset_login):
    User.create("username", "email", "password")

    response = client.post(
        "/login",
        data={"email": "email", "password": "invalid_password"},
    )

    assert response.status_code == 302
    assert response.location == url_for("auth.login")
    assert not current_user.is_authenticated


def test_login_invalid_form(db_session, client, reset_login, captured_templates):
    response = client.post("/login")

    assert response.status_code == 200
    assert captured_templates[0][0].name == "auth/login.html"
    assert isinstance(captured_templates[0][1]["form"], LoginForm)
    assert captured_templates[0][1]["form"].errors == {
        "email": ["This field is required."],
        "password": ["This field is required."],
    }
    assert not current_user.is_authenticated
