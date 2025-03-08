from __future__ import annotations
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.balance import Balance
    from app.model.group import Group

from app.enum import FormEnum
from datetime import datetime
from sqlalchemy.orm import Mapped, relationship

from app.database import db
from app.model.constants import NO_GROUP
from app.splits import SplitType


class ExpenseCategory(FormEnum):
    ACCOMMODATION = "Accommodation"
    DRINKS = "Drinks"
    ENTERTAINMENT = "Entertainment"
    FOOD = "Food"
    GAS = "Gas"
    GROCERIES = "Groceries"
    OTHER = "Other"
    TICKETS = "Tickets"
    UTILITIES = "Utilities"


class Expense(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    amount: Mapped[float] = db.mapped_column(nullable=False)
    balances: Mapped[list[Balance]] = relationship(back_populates="expense")
    description: Mapped[str] = db.mapped_column(nullable=True)
    category: Mapped[ExpenseCategory] = db.mapped_column(
        nullable=True, default=ExpenseCategory.OTHER
    )
    split: Mapped[SplitType] = db.mapped_column(nullable=False)
    group_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("group.id"), nullable=True, default=NO_GROUP
    )
    group: Mapped[Group] = relationship(back_populates="expenses")
    creator_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    creator: Mapped[User] = relationship(foreign_keys=[creator_id])
    created_at: Mapped[datetime] = db.mapped_column(default=datetime.now())
    updater_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=True)
    updater: Mapped[User] = relationship(foreign_keys=[updater_id])
    updated_at: Mapped[datetime] = db.mapped_column(
        onupdate=datetime.now(), nullable=True
    )

    @classmethod
    def create(
        cls,
        amount: float,
        balances: list[Balance],
        creator_id: int,
        split: SplitType,
        group: Group | None = None,
        description: str | None = None,
        category: ExpenseCategory | None = None,
    ) -> Self:
        expense = cls(
            amount=amount,
            balances=balances,
            creator_id=creator_id,
            split=split,
            group=group,
            description=description,
            category=category,
        )
        db.session.add(expense)
        db.session.flush()
        return expense
