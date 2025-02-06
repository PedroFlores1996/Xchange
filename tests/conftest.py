import pytest
from . import setup_db, teardown_db, clean_db
from app import create_app
from app.config import TestConfig
from app import database


@pytest.fixture(scope="session")
def app():
    """Fixture to create the Flask application for the test session."""
    app = create_app(config=TestConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def db(app):
    """Fixture to set up the database for the test session."""
    setup_db(app)
    yield database.db
    teardown_db()


@pytest.fixture(scope="function")
def db_session(db):
    """Fixture to provide a clean database session for each test function."""
    clean_db()
    yield db.session
    db.session.rollback()
    db.session.close()


@pytest.fixture(scope="session")
def client(app):
    """Fixture to provide a test client for the Flask application."""
    with app.test_client() as client:
        yield client
