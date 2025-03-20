from app.model.expense import Expense


def update_users_expenses(expense: Expense) -> None:
    for balance in expense.balances:
        balance.user.add_expense(expense)
    if expense not in expense.creator.expenses:
        expense.creator.add_expense(expense)
