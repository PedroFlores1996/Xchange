from app import create_app
from app.config import Config


class DummyConfig:
    TESTING = True
    SECRET_KEY = "dummy"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:dummy:"


def test_create_app_with_config():
    app = create_app(DummyConfig)
    assert app.config["TESTING"] is DummyConfig.TESTING
    assert app.config["SECRET_KEY"] == DummyConfig.SECRET_KEY
    assert app.config["SQLALCHEMY_DATABASE_URI"] == DummyConfig.SQLALCHEMY_DATABASE_URI


def test_create_app_without_config():
    app = create_app()
    # Should use default config; at least Flask's SECRET_KEY should be set
    assert not app.config["TESTING"]
    assert app.config["SECRET_KEY"] == Config.SECRET_KEY
    assert app.config["SQLALCHEMY_DATABASE_URI"] == Config.SQLALCHEMY_DATABASE_URI
