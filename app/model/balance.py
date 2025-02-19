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
    user: Mapped[User] = relationship(back_populates="balances")
    expense_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("expense.id"), nullable=False
    )
    expense: Mapped[Expense] = relationship(back_populates="balances")
    owed_amount: Mapped[float] = db.mapped_column(nullable=False)
    lent_amount: Mapped[float] = db.mapped_column(nullable=False)
    total_amount: Mapped[float] = db.mapped_column(nullable=False)
    positive: Mapped[bool] = db.mapped_column(nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "expense_id", "positive"),)

    def create(cls, user: User, expense: Expense, amount: float) -> Self:
        new_balance = cls(
            user=user,
            expense=expense,
            amount=amount,
            positive=True if amount > 0 else False,
        )
        db.session.add(new_balance)
        db.session.commit()
        return new_balance
