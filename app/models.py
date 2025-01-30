from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def create_user(username, password):
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def check_credentials(username, password):
        user = User.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return False

    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()