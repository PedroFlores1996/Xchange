from flask import url_for
from flask_login import login_user  #
from app.model.user import User


def test_logged_out_authenticated(db_session, client, reset_login):
    user = User.create("user1", "password1")
    login_user(user)

    response = client.get("/login")

    assert response.status_code == 302
    assert response.location == url_for("index.home_page")


def test_logged_out_not_authenticated(client, reset_login, captured_templates):
    response = client.get("/login")

    assert response.status_code == 200
    assert len(captured_templates) == 1
    assert captured_templates[0][0].name == "auth/login.html"
