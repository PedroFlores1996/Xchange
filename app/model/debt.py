from __future__ import annotations
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.group import Group

from sqlalchemy.orm import Mapped, relationship
from app.database import db
from app.model.constants import NO_GROUP


class Debt(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    lender_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    lender: Mapped[User] = relationship(
        foreign_keys=[lender_id], back_populates="lender_debts"
    )
    borrower_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("user.id"), nullable=False
    )
    borrower: Mapped[User] = relationship(
        foreign_keys=[borrower_id], back_populates="borrower_debts"
    )
    amount: Mapped[float] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=True)
    group_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("group.id"), nullable=True, default=NO_GROUP
    )
    group: Mapped[Group] = relationship(back_populates="debts")
    __table_args__ = (db.UniqueConstraint("lender_id", "borrower_id", "group_id"),)

    @classmethod
    def find(
        cls, lender: User, borrower: User, group: Group | None = None
    ) -> Self | None:
        return cls.query.filter_by(
            lender_id=lender.id,
            borrower_id=borrower.id,
            group_id=group.id if group else NO_GROUP,
        ).first()

    @classmethod
    def __find_reversed(
        cls, lender: User, borrower: User, group: Group | None = None
    ) -> Self | None:
        return cls.find(borrower, lender, group)

    @classmethod
    def update(
        cls,
        lender: User,
        borrower: User,
        amount: float,
        description: str | None = None,
        group: Group | None = None,
    ) -> None:
        if existing_debt := cls.find(lender, borrower, group):
            existing_debt.amount += amount
            db.session.flush()
            return

        if reverse_debt := cls.__find_reversed(lender, borrower, group):
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
            lender=lender,
            borrower=borrower,
            amount=amount,
            description=description,
            group=group,
        )
        db.session.add(new_debt)
        db.session.flush()
        return
