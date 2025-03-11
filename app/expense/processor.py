from flask_login import current_user

from app.database import db
from app.model.expense import Expense
from app.model.debt import Debt
from app.expense.mapper import ExpenseData
from app.model.balance import Balance
from app.split.constants import OWED, PAYED, TOTAL
from app.split import split
from app.debt import update_debts


def map_balances(balances: dict[int, dict[str, float]]) -> list[Balance]:
    return [
        Balance.create(
            user_id=user_id,
            owed=balance[OWED],
            payed=balance[PAYED],
            total=balance[TOTAL],
        )
        for user_id, balance in balances.items()
    ]


def create_expense(data: ExpenseData, balances: dict[int, dict[str, float]]) -> Expense:
    return Expense.create(
        amount=data.amount,
        description=data.description,
        creator_id=current_user.get_id(),
        category=data.category,
        payers_split=data.payers_split,
        owers_split=data.owers_split,
        group_id=data.group_id,
        balances=map_balances(balances),
    )


def create_expense_from(data: ExpenseData) -> Expense:
    balances = split(
        data.amount, data.payers, data.owers, data.payers_split, data.owers_split
    )
    update_debts(balances)
    expense = create_expense(data, balances)
    db.session.commit()
    return expense
