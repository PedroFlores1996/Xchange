from __future__ import annotations
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.expense import Expense

from sqlalchemy.orm import Mapped, relationship
from app.database import db


class Balance(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    user_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship()
    expense_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("expense.id"), nullable=False
    )
    expense: Mapped[Expense] = relationship(back_populates="balances")
    owed_amount: Mapped[float] = db.mapped_column(nullable=False)
    payed_amount: Mapped[float] = db.mapped_column(nullable=False)
    total_amount: Mapped[float] = db.mapped_column(nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "expense_id"),)

    @classmethod
    def create(cls, user: User, owed_amount: float, payed_amount: float) -> Self:
        new_balance = cls(
            user=user,
            owed_amount=owed_amount,
            payed_amount=payed_amount,
            total_amount=payed_amount - owed_amount,
        )
        return new_balance
