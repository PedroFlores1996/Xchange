from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.expense import Expense
    from app.model.group_balance import GroupBalance

from sqlalchemy.orm import Mapped, relationship
from app.database import db


# Association table
group_members = db.Table(
    "group_members",
    db.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("group_id", db.ForeignKey("group.id"), primary_key=True),
)


class Group(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    name: Mapped[str] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=True)
    users: Mapped[List[User]] = relationship(
        secondary=group_members, back_populates="groups"
    )
    expenses: Mapped[List[Expense]] = relationship(back_populates="group")
    group_balances: Mapped[List[GroupBalance]] = relationship(back_populates="group")

    @classmethod
    def create(
        cls, name: str, users: List[User], description: str | None = None
    ) -> Group:
        if not users:
            raise ValueError("The users list cannot be empty.")
        new_group = cls(name=name, users=users, description=description)
        db.session.add(new_group)
        db.session.commit()
        return new_group

    def update_description(self, description: str) -> Group:
        self.description = description
        db.session.commit()
        return self

    def add_user(self, user: User) -> Group:
        if user not in self.users:
            self.users.append(user)
            db.session.commit()
        return self

    def add_users(self, users: List[User]) -> Group:
        for user in users:
            self.add_user(user)
        return self

    def remove_user(self, user: User) -> Group:
        if user in self.users:
            self.users.remove(user)
            db.session.commit()
        if not self.users:
            db.session.delete(self)
            db.session.commit()
        return self
