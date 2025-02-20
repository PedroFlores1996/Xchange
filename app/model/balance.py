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
    borrowed_amount: Mapped[float] = db.mapped_column(nullable=False)
    lent_amount: Mapped[float] = db.mapped_column(nullable=False)
    total_amount: Mapped[float] = db.mapped_column(nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "expense_id"),)

    @classmethod
    def create(
        cls, user: User, expense: Expense, borrowed_amount: float, lent_amount: float
    ) -> Self:
        new_balance = cls(
            user=user,
            expense=expense,
            borrowed_amount=borrowed_amount,
            lent_amount=lent_amount,
            total_amount=lent_amount - borrowed_amount,
        )
        db.session.add(new_balance)
        db.session.commit()
        return new_balance
