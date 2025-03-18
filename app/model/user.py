from __future__ import annotations
from typing import TYPE_CHECKING, Self, List

if TYPE_CHECKING:
    from app.model.group import Group
    from app.model.debt import Debt

from sqlalchemy.orm import Mapped, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.database import db

# Association table for the friends relationship
friends = db.Table(
    "friends",
    db.Model.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("friend_id", db.ForeignKey("user.id"), primary_key=True),
)


class User(db.Model, UserMixin):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    email: Mapped[str] = db.mapped_column(unique=True, nullable=False)
    username: Mapped[str] = db.mapped_column(nullable=False)
    password: Mapped[str] = db.mapped_column(nullable=False)
    groups: Mapped[List[Group]] = relationship(
        secondary="group_members", back_populates="users"
    )
    lender_debts: Mapped[List[Debt]] = relationship(
        foreign_keys="Debt.lender_id", back_populates="lender"
    )
    borrower_debts: Mapped[List[Debt]] = relationship(
        foreign_keys="Debt.borrower_id", back_populates="borrower"
    )
    friends: Mapped[List[User]] = relationship(
        "User",
        secondary=friends,
        primaryjoin=id == friends.c.user_id,
        secondaryjoin=id == friends.c.friend_id,
        backref="friends_with",
    )

    @classmethod
    def create(cls, username: str, email: str, password: str) -> Self:
        hashed_password: str = generate_password_hash(password)
        new_user: Self = cls(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def authenticate(cls, email: str, password: str) -> Self | None:
        user: User | None = cls.get_user_by_email(email)
        if user and check_password_hash(user.password, password):
            return user
        return None

    @classmethod
    def get_user_by_id(cls, user_id: int) -> Self | None:
        return cls.query.get(user_id)

    @classmethod
    def get_user_by_email(cls, email: str) -> Self | None:
        return cls.query.filter_by(email=email).first()

    def add_to_group(self, group: Group) -> None:
        if group not in self.groups:
            self.groups.append(group)
            db.session.commit()

    def remove_from_group(self, group: Group) -> None:
        if group in self.groups:
            group.remove_user(self)

    def add_friends(self, *friends: User) -> None:
        for friend in friends:
            if friend not in self.friends:
                self.friends.append(friend)
                friend.add_friends(self)
        db.session.commit()

    def remove_friends(self, *friends: User) -> None:
        for friend in friends:
            if friend in self.friends:
                self.friends.remove(friend)
                friend.remove_friends(self)
        db.session.commit()
