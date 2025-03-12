from flask_login import current_user

from app.database import db
from app.model.expense import Expense
from app.expense.mapper import ExpenseData, map_balances_to_model
from app.split import split
from app.debt import update_debts


def create_expense(data: ExpenseData, balances: dict[int, dict[str, float]]) -> Expense:
    return Expense.create(
        amount=data.amount,
        description=data.description,
        creator_id=current_user.get_id(),
        category=data.category,
        payers_split=data.payers_split,
        owers_split=data.owers_split,
        group_id=data.group_id,
        balances=map_balances_to_model(balances),
    )


def submit_expense(data: ExpenseData) -> Expense:
    balances = split(
        data.amount, data.payers, data.owers, data.payers_split, data.owers_split
    )
    update_debts(balances)
    expense = create_expense(data, balances)
    db.session.commit()
    return expense
