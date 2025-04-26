from flask_login import current_user
from app.model.expense import Expense
from app.model.user import User
from app.model.constants import NO_GROUP


def update_expense_in_users(expense: Expense) -> None:
    for balance in expense.balances:
        balance.user.add_expense(expense)
    if expense not in expense.creator.expenses:
        expense.creator.add_expense(expense)


def update_expenses_in_users(expenses: list[Expense]) -> None:
    for expense in expenses:
        update_expense_in_users(expense)


def get_user_balances(user: User) -> tuple[dict[int, float], float]:
    group_balances = dict.fromkeys([group.id for group in user.groups], 0)
    group_balances[NO_GROUP] = 0
    overall_balance = 0
    for debt in current_user.lender_debts:
        group_balances[debt.group_id] += debt.amount
        overall_balance += debt.amount
    for debt in current_user.borrower_debts:
        group_balances[debt.group_id] -= debt.amount
        overall_balance -= debt.amount
    return group_balances, overall_balance
