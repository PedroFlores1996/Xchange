from flask import url_for
from flask_login import current_user  #
from app.auth.forms import SigninForm
from app.model.user import User


def test_get_signin_form(client, captured_templates):
    response = client.get("/signin")

    assert response.status_code == 200
    assert len(captured_templates) == 1
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)


def test_post_username_not_alphanumeric(
    db_session, client, reset_login, captured_templates
):
    response = client.post(
        "/signin",
        data={
            "username": "username!",
            "email": "email",
            "password": "password",
            "confirm_password": "password",
        },
    )

    assert User.query.count() == 0
    assert response.status_code == 200
    assert captured_templates[0][0].name == "auth/signin.html"
    assert isinstance(captured_templates[0][1]["form"], SigninForm)
    assert captured_templates[0][1]["form"].errors == {
        "username": ["Username must contain only letters and numbers."]
    }
    assert not current_user.is_authenticated


def test_post_password_mismatch(db_session, client, reset_login, captured_templates):
    response = client.post(
        "/signin",
        data={
            "username": "username",
            "email": "email",
            "password": "password1",
            "confirm_password": "password2",
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


def test_post_valid_form(db_session, client, reset_login):
    response = client.post(
        "/signin",
        data={
            "username": "username",
            "email": "email",
            "password": "password",
            "confirm_password": "password",
        },
    )

    assert response.status_code == 302
    assert response.location == url_for("index.home_page")
    assert User.query.count() == 1
    assert current_user.is_authenticated


def test_post_valid_form_with_existing_user(db_session, client, reset_login):
    User.create("username", "email", "password")

    response = client.post(
        "/signin",
        data={
            "username": "username",
            "email": "email",
            "password": "password",
            "confirm_password": "password",
        },
    )

    assert User.query.count() == 1
    with client.session_transaction() as session:
        assert "Email already exists" in session["_flashes"][0]
    assert response.status_code == 302
    assert response.location == url_for("auth.signin")
    assert not current_user.is_authenticated
