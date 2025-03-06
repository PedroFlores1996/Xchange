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
    owed: Mapped[float] = db.mapped_column(nullable=False)
    payed: Mapped[float] = db.mapped_column(nullable=False)
    total: Mapped[float] = db.mapped_column(nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "expense_id"),)

    @classmethod
    def create(cls, user_id: int, owed: float, payed: float, total) -> Self:
        new_balance = cls(
            user_id=user_id,
            owed=owed,
            payed=payed,
            total=total,
        )
        return new_balance
