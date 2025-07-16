from __future__ import annotations
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from app.model.user import User

from sqlalchemy.orm import Mapped, relationship
from app.database import db


class Debt(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    borrower_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("user.id"), nullable=False
    )
    borrower: Mapped[User] = relationship(
        foreign_keys=[borrower_id], back_populates="borrower_debts"
    )
    lender_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    lender: Mapped[User] = relationship(
        foreign_keys=[lender_id], back_populates="lender_debts"
    )
    amount: Mapped[float] = db.mapped_column(nullable=False)
    __table_args__ = (db.UniqueConstraint("lender_id", "borrower_id"),)

    @classmethod
    def find(
        cls, borrower_id: int, lender_id: int
    ) -> Self | None:
        return cls.query.filter_by(
            borrower_id=borrower_id,
            lender_id=lender_id,
        ).first()

    @classmethod
    def __find_reversed(
        cls, borrower_id: int, lender_id: int
    ) -> Self | None:
        return cls.find(lender_id, borrower_id)

    @classmethod
    def update(
        cls,
        borrower_id: int,
        lender_id: int,
        amount: float,
    ) -> None:
        if existing_debt := cls.find(borrower_id, lender_id):
            existing_debt.amount += amount
            db.session.flush()
            return

        if reverse_debt := cls.__find_reversed(borrower_id, lender_id):
            if reverse_debt.amount == amount:
                db.session.delete(reverse_debt)
                db.session.flush()
                return
            elif reverse_debt.amount > amount:
                reverse_debt.amount -= amount
                db.session.flush()
                return
            else:
                amount -= reverse_debt.amount
                db.session.delete(reverse_debt)
                db.session.flush()

        new_debt = cls(
            borrower_id=borrower_id,
            lender_id=lender_id,
            amount=amount,
        )
        db.session.add(new_debt)
        db.session.flush()
        return
