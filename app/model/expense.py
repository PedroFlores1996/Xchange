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
from app.split import SplitType


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


expense_users = db.Table(
    "expense_users",
    db.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("expense_id", db.ForeignKey("expense.id"), primary_key=True),
)


class Expense(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    amount: Mapped[float] = db.mapped_column(nullable=False)
    balances: Mapped[list[Balance]] = relationship(back_populates="expense")
    description: Mapped[str] = db.mapped_column(nullable=True)
    category: Mapped[ExpenseCategory] = db.mapped_column(nullable=True)
    payers_split: Mapped[SplitType] = db.mapped_column(
        nullable=False, default=SplitType.EQUALLY
    )
    owers_split: Mapped[SplitType] = db.mapped_column(
        nullable=False, default=SplitType.EQUALLY
    )
    group_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("group.id"), nullable=True, default=NO_GROUP
    )
    group: Mapped[Group] = relationship(back_populates="expenses")
    users: Mapped[list[User]] = relationship(
        "User",
        secondary="expense_users",
        back_populates="expenses",
        overlaps="expenses",
    )
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
        payers_split: SplitType | None = None,
        owers_split: SplitType | None = None,
        group_id: int | None = None,
        description: str | None = None,
        category: ExpenseCategory | None = None,
    ) -> Self:
        expense = cls(
            amount=amount,
            balances=balances,
            creator_id=creator_id,
            payers_split=payers_split,
            owers_split=owers_split,
            group_id=group_id,
            description=description,
            category=category,
        )
        db.session.add(expense)
        db.session.flush()
        return expense
