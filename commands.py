from flask_script import Manager

from app.database import db

manager = Manager()

@manager.command
def create():
    db.create_all()

@manager.command
def drop():
    db.drop_all()

if __name__ == "__main__":
    manager.run()