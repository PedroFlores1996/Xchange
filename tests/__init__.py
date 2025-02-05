from app.database import db


def setup_db(app):
    db.app = app
    db.create_all()


def teardown_db():
    db.session.remove()
    db.drop_all()
    if db.session.bind:
        db.session.bind.dispose()


def clean_db():
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
