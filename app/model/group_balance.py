from __future__ import annotations
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.group import Group

from sqlalchemy.orm import Mapped, relationship
from app.database import db


class GroupBalance(db.Model):  # type: ignore
    """
    Represents a user's balance within a specific group.
    Positive balance means the user is owed money by the group.
    Negative balance means the user owes money to the group.
    """

    id: Mapped[int] = db.mapped_column(primary_key=True)
    user_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="group_balances")
    group_id: Mapped[int] = db.mapped_column(db.ForeignKey("group.id"), nullable=False)
    group: Mapped[Group] = relationship(back_populates="group_balances")
    balance: Mapped[float] = db.mapped_column(nullable=False, default=0.0)

    __table_args__ = (db.UniqueConstraint("user_id", "group_id"),)

    @classmethod
    def find(cls, user_id: int, group_id: int) -> Self | None:
        """Find a group balance record for a specific user and group."""
        return cls.query.filter_by(user_id=user_id, group_id=group_id).first()

    @classmethod
    def find_or_create(cls, user_id: int, group_id: int) -> Self:
        """Find or create a group balance record for a specific user and group."""
        if balance := cls.find(user_id, group_id):
            return balance

        balance = cls(user_id=user_id, group_id=group_id, balance=0.0)
        db.session.add(balance)
        db.session.flush()
        return balance

    @classmethod
    def update_balance(cls, user_id: int, group_id: int, amount: float) -> None:
        """Update a user's balance in a group by adding the specified amount."""
        balance = cls.find_or_create(user_id, group_id)
        balance.balance += amount
        db.session.flush()

    @classmethod
    def set_balance(cls, user_id: int, group_id: int, amount: float) -> None:
        """Set a user's balance in a group to the specified amount."""
        balance = cls.find_or_create(user_id, group_id)
        balance.balance = amount
        db.session.commit()

    @classmethod
    def get_group_balances(cls, group_id: int) -> dict[int, float]:
        """Get all user balances for a specific group."""
        balances = cls.query.filter_by(group_id=group_id).all()
        return {balance.user_id: balance.balance for balance in balances}

    @classmethod
    def clear_group_balances(cls, group_id: int) -> None:
        """Clear all balances for a specific group (used for settlement)."""
        cls.query.filter_by(group_id=group_id).delete()
        db.session.commit()
