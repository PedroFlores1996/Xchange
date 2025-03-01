from app.model.expense import Expense
from app.expense.mapper import ExpenseData
from app.splits import equally, amount, percentage
from app.splits.types import SplitType


def process_expense(data: ExpenseData) -> Expense:
    balances = get_balances(data)
    update_debts(balances)
    expense = create_expense(data, balances)
    return expense
