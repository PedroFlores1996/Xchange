from flask_login import LoginManager
from app.database import db
from app.model.user import User


loginManager = LoginManager()


@loginManager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
