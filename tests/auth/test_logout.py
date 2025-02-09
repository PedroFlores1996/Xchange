from flask import url_for
from flask_login import current_user


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
