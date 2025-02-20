from __future__ import annotations
from typing import TYPE_CHECKING, Self, List

if TYPE_CHECKING:
    from app.model.user import User
    from app.model.balance import Balance
    from app.model.group import Group

from datetime import datetime
from sqlalchemy.orm import Mapped, relationship

from app.database import db
from enum import Enum


class ExpenseType(Enum):
    ACCOMMODATION = "accommodation"
    DRINKS = "drinks"
    ENTERTAINMENT = "entertainment"
    FOOD = "food"
    GAS = "gas"
    GROCERIES = "groceries"
    OTHER = "other"
    TICKETS = "tickets"
    UTILITIES = "utilities"


class Expense(db.Model):  # type: ignore
    id: Mapped[int] = db.mapped_column(primary_key=True)
    amount: Mapped[float] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=False)
    type: Mapped[ExpenseType] = db.mapped_column(nullable=True)
    balances: Mapped[List[Balance]] = relationship()
    group_id: Mapped[int] = db.mapped_column(db.ForeignKey("group.id"), nullable=False)
    group: Mapped[Group] = relationship(back_populates="expenses")
    creator_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    creator: Mapped[User] = relationship(foreign_keys=[creator_id])
    created_at: Mapped[datetime] = db.mapped_column(default=datetime.now())
    updater_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=True)
    updater: Mapped[User] = relationship(foreign_keys=[updater_id])
    updated_at: Mapped[datetime] = db.mapped_column(onupdate=datetime.now())
