from flask_login import current_user
from app.debt import get_debts_total_balance
from app.model import Debt, User, Expense
from app.model.constants import NO_GROUP
from app.model.group import Group
from app.split.constants import OWED, PAYED, TOTAL


def get_authorized_group(group_id: int) -> Group | None:
    """
    Finds the user's group that matches the group_id and returns all members in it.

    :param user: The user object
    :param group_id: The ID of the group to search for
    :return: The list of members in the group, or None if the group is not found
    """
    return next((g for g in current_user.groups if g.id == group_id), None)


def get_group_user_debts(
    group: Group,
) -> dict[int, dict[str, list[Debt] | float]]:
    group_debts = {user.id: {PAYED: [], OWED: [], TOTAL: 0.0} for user in group.users}
    # Iterate through all debts in the group
    for debt in group.debts:
        # Lender
        group_debts[debt.lender.id][PAYED].append(debt)
        group_debts[debt.lender.id][TOTAL] += float(debt.amount)

        # Borrower
        group_debts[debt.borrower.id][OWED].append(debt)
        group_debts[debt.borrower.id][TOTAL] -= float(debt.amount)
    return group_debts


def get_no_group_debts(user: User):
    return [debt for debt in user.lender_debts if debt.group_id == NO_GROUP] + [
        debt for debt in user.borrower_debts if debt.group_id == NO_GROUP
    ]


def get_no_group_user_balances(
    user: User,
) -> dict[str, list[Debt] | float]:
    no_group_debts = get_no_group_debts(user)
    user_debts = {}
    for debt in no_group_debts:
        if user.id == debt.lender_id:
            user_debts[debt.borrower_id] = debt.amount
        else:
            user_debts[debt.lender_id] = -debt.amount
    return user_debts


def get_group_user_expenses(
    user: User,
    group_id: int,
) -> list[Expense]:
    return sorted(
        [expense for expense in user.expenses if (expense.group_id == group_id)],
        key=lambda e: e.created_at,
        reverse=True,
    )


def get_group_user_balances(group: Group) -> dict[User, float]:
    """
    Returns a dictionary of users and their balances in the group.
    The balance is calculated as the total amount paid minus the total amount owed.
    """
    user_balances: dict[User, float] = {}
    for debt in group.debts:
        user_balances[debt.lender] = user_balances.get(debt.lender, 0.0) + float(
            debt.amount
        )
        user_balances[debt.borrower] = user_balances.get(debt.borrower, 0.0) - float(
            debt.amount
        )
    return user_balances
