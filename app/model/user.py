from sqlalchemy import Column, Integer, String, Float
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.database import db
from .group import group_members

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    groups = db.relationship("Group", secondary=group_members, back_populates='users')
    lender_debts = db.relationship("Debt", foreign_keys='Debt.lender_id', back_populates='lender')
    borrower_debts = db.relationship("Debt", foreign_keys='Debt.borrower_id', back_populates='borrower')

    def create_user(username, password):
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def authenticate(username, password):
        user = User.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return False

    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()