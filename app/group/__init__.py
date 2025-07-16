from flask_login import current_user
from app.debt import get_debts_total_balance
from app.model import Debt, User, Expense
from app.model.group_balance import GroupBalance
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
    """
    Returns group user debts. Since debts are now stored in GroupBalance,
    this function creates a structure compatible with the old format for backward compatibility.
    """
    group_debts = {user.id: {PAYED: [], OWED: [], TOTAL: 0.0} for user in group.users}
    
    # Get balances from GroupBalance model
    for group_balance in group.group_balances:
        group_debts[group_balance.user_id][TOTAL] = group_balance.balance
        
    return group_debts


def get_no_group_debts(user: User):
    """
    Returns all individual debts for a user. Since debts are now only individual (no group_id),
    this returns all debts.
    """
    return list(user.lender_debts) + list(user.borrower_debts)


def get_no_group_user_balances(
    user: User,
) -> dict[str, list[Debt] | float]:
    """
    Returns individual (non-group) debt balances for a user.
    Since debts are now only individual, this returns all debt balances.
    """
    individual_debts = get_no_group_debts(user)
    user_debts = {}
    for debt in individual_debts:
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
    The balance is retrieved from the GroupBalance model.
    Users without a GroupBalance record are assumed to have zero balance.
    """
    user_balances: dict[User, float] = {}
    
    # Initialize all group users with zero balance
    for user in group.users:
        user_balances[user] = 0.0
    
    # Update with actual balances from GroupBalance records
    for group_balance in group.group_balances:
        user_balances[group_balance.user] = group_balance.balance
    
    return user_balances
