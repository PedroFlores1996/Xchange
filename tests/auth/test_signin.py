from flask import url_for
from flask_login import current_user
from app.auth.forms import SigninForm
from app.model.user import User


def test_signin_get(client, captured_templates):
    response = client.get("/signin")

    assert response.status_code == 200
    assert len(captured_templates) == 1
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)


def test_signin_post(db_session, client, reset_login, csrf_token):
    response = client.post(
        "/signin",
        data={
            "username": "user1",
            "password": "password1",
            "confirm_password": "password1",
            "csrf_token": csrf_token,
        },
    )

    assert response.status_code == 302
    assert response.location == url_for("index.home_page")
    assert User.query.count() == 1
    assert current_user.is_authenticated


def test_signin_post_existing_user(db_session, client, reset_login, csrf_token):
    User.create("user1", "password1")

    response = client.post(
        "/signin",
        data={
            "username": "user1",
            "password": "password1",
            "confirm_password": "password1",
            "csrf_token": csrf_token,
        },
    )

    assert User.query.count() == 1
    with client.session_transaction() as session:
        assert "Username already exists" in session["_flashes"][0]
    assert response.status_code == 302
    assert response.location == url_for("auth.signin")
    assert not current_user.is_authenticated


def test_signin_post_password_mismatch(
    db_session, client, reset_login, csrf_token, captured_templates
):
    response = client.post(
        "/signin",
        data={
            "username": "user1",
            "password": "password1",
            "confirm_password": "password2",
            "csrf_token": csrf_token,
        },
    )

    assert User.query.count() == 0
    assert response.status_code == 200
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)
    assert captured_templates[0][1]["form"].errors == {
        "confirm_password": ["Passwords must match"]
    }
    assert not current_user.is_authenticated


def test_signin_post_missing_csrf_token(
    db_session, client, reset_login, captured_templates
):
    response = client.post(
        "/signin",
        data={
            "username": "user1",
            "password": "password1",
            "confirm_password": "password1",
        },
    )

    assert User.query.count() == 0
    assert response.status_code == 200
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)
    assert captured_templates[0][1]["form"].errors == {
        "csrf_token": ["The CSRF token is missing."]
    }
    assert not current_user.is_authenticated


def test_signin_post_invalid_form(
    db_session, client, reset_login, csrf_token, captured_templates
):
    response = client.post(
        "/signin",
        data={"csrf_token": csrf_token},
    )

    assert User.query.count() == 0
    assert response.status_code == 200
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)
    assert captured_templates[0][1]["form"].errors == {
        "username": ["This field is required."],
        "password": ["This field is required."],
        "confirm_password": ["This field is required."],
    }
    assert not current_user.is_authenticated
