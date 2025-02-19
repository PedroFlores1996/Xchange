from __future__ import annotations
from typing import TYPE_CHECKING, Self, List

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.balance import Balance

from datetime import datetime
from sqlalchemy.orm import Mapped, relationship

from app.database import db


class Expense(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    amount: Mapped[float] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=False)
    creator_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    creator: Mapped[User] = relationship(foreign_keys=[creator_id])
    created_at: Mapped[datetime] = db.mapped_column(default=datetime.now())
    updated_by_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("user.id"), nullable=True
    )
    updated_by: Mapped[User] = relationship(foreign_keys=[updated_by_id])
    updated_at: Mapped[datetime] = db.mapped_column(onupdate=datetime.now())
    balances: Mapped[List[Balance]] = relationship(back_populates="expense")

    def create(cls, amount: float, description: str, creator: User) -> Self:
        new_expense = cls(amount=amount, description=description, creator=creator)
        db.session.add(new_expense)
        db.session.commit()
        return new_expense
