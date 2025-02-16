from sqlalchemy.orm import Mapped
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.database import db


class User(db.Model, UserMixin):
    id: Mapped[int] = db.mapped_column(primary_key=True)
    username: Mapped[str] = db.mapped_column(unique=True, nullable=False)
    password: Mapped[str] = db.mapped_column(nullable=False)
    groups = db.relationship("Group", secondary="group_members", back_populates="users")
    lender_debts = db.relationship(
        "Debt", foreign_keys="Debt.lender_id", back_populates="lender"
    )
    borrower_debts = db.relationship(
        "Debt", foreign_keys="Debt.borrower_id", back_populates="borrower"
    )

    @classmethod
    def create(cls, username, password):
        hashed_password = generate_password_hash(password)
        new_user = cls(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return False

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def add_to_group(self, group):
        if group not in self.groups:
            self.groups.append(group)
            db.session.commit()

    def remove_from_group(self, group):
        if group in self.groups:
            group.remove_user(self)
