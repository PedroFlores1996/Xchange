from flask_login import current_user
from app.debt import get_debts_total_balance, simplify_debts
from app.model import Debt, User, Expense
from app.model.group_balance import GroupBalance
from app.model.group import Group
from app.split.constants import OWED, PAYED, TOTAL
from app.expense import ExpenseData
from app.model.expense import ExpenseCategory
from app.split import SplitType
from app.expense.submit import submit_expense
from app.database import db


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


def validate_user_in_group(group: Group, user_id: int) -> User | None:
    """
    Validates that a user exists and is a member of the given group.
    Returns the User object if valid, None otherwise.
    """
    user = db.session.get(User, user_id)
    if not user or user not in group.users:
        return None
    return user


def check_group_has_balances(group: Group) -> bool:
    """
    Checks if the group has any non-zero balances that can be settled.
    Returns True if there are balances to settle, False otherwise.
    """
    group_balances = get_group_user_balances(group)
    return any(balance != 0 for balance in group_balances.values())


def calculate_group_settlement_transactions(group: Group) -> list[dict]:
    """
    Calculates settlement transactions for settling all debts in a group.
    Returns a list of transaction dictionaries with debtor, creditor, amount, and description.
    """
    group_balances = get_group_user_balances(group)
    balance_dict = {user.id: balance for user, balance in group_balances.items()}
    transactions = simplify_debts(balance_dict)
    
    settlement_transactions = []
    for debtor_id, creditor_id, amount in transactions:
        debtor = db.session.get(User, debtor_id)
        creditor = db.session.get(User, creditor_id)
        settlement_transactions.append({
            "debtor": debtor,
            "creditor": creditor,
            "amount": amount,
            "description": f"Settlement payment from {debtor.username} to {creditor.username}",
        })
    
    return settlement_transactions


def calculate_individual_settlement_transactions(group: Group, user: User) -> list[dict]:
    """
    Calculates settlement transactions for settling an individual user's balance within a group.
    Returns a list of transaction dictionaries with payer, receiver, amount, and description.
    """
    group_balances = get_group_user_balances(group)
    user_balance = group_balances.get(user)
    
    if not user_balance or user_balance == 0:
        return []
    
    settlement_transactions = []
    remaining_debt = abs(user_balance)
    
    if user_balance > 0:
        # User is owed money - find who owes money (negative balances) to pay this user
        debtors = [(u, abs(balance)) for u, balance in group_balances.items() 
                   if u != user and balance < 0]
        debtors.sort(key=lambda x: x[1], reverse=True)  # Sort by debt amount descending
        
        for debtor, debt_amount in debtors:
            if remaining_debt <= 0:
                break
            
            payment_amount = min(remaining_debt, debt_amount)
            settlement_transactions.append({
                'payer': debtor,
                'receiver': user,
                'amount': payment_amount,
                'description': f"Settlement: {debtor.username} pays {user.username}"
            })
            remaining_debt -= payment_amount
    
    else:
        # User owes money - find who is owed money (positive balances) to receive from this user
        creditors = [(u, balance) for u, balance in group_balances.items() 
                     if u != user and balance > 0]
        creditors.sort(key=lambda x: x[1], reverse=True)  # Sort by credit amount descending
        
        for creditor, credit_amount in creditors:
            if remaining_debt <= 0:
                break
            
            payment_amount = min(remaining_debt, credit_amount)
            settlement_transactions.append({
                'payer': user,
                'receiver': creditor,
                'amount': payment_amount,
                'description': f"Settlement: {user.username} pays {creditor.username}"
            })
            remaining_debt -= payment_amount
    
    return settlement_transactions


def create_settlement_expenses_from_transactions(settlement_transactions: list[dict], group_id: int, creator_id: int | None = None) -> list[Expense]:
    """
    Creates settlement expenses from a list of settlement transactions.
    Returns a list of created Expense objects.
    """
    if creator_id is None:
        creator_id = current_user.id
        
    settlement_expenses = []
    for transaction in settlement_transactions:
        # Handle both formats: group settlement uses 'debtor'/'creditor', individual uses 'payer'/'receiver'
        payer = transaction.get('payer') or transaction.get('debtor')
        receiver = transaction.get('receiver') or transaction.get('creditor')
        
        if not payer or not receiver:
            continue  # Skip invalid transactions
        
        expense_data = ExpenseData(
            description=transaction['description'],
            amount=transaction['amount'],
            creator_id=creator_id,
            group_id=group_id,
            category=ExpenseCategory.SETTLEMENT,
            payers_split=SplitType.AMOUNT,
            owers_split=SplitType.AMOUNT,
            payers={payer.id: transaction['amount']},
            owers={receiver.id: transaction['amount']},
        )
        
        settlement_expense = submit_expense(expense_data)
        settlement_expenses.append(settlement_expense)
    
    return settlement_expenses


def create_group_settlement_expenses(group: Group) -> list[Expense]:
    """
    Creates settlement expenses for settling all debts in a group.
    Returns a list of created Expense objects.
    """
    settlement_transactions = calculate_group_settlement_transactions(group)
    # Use current_user.id if available, otherwise use the first user in the group
    creator_id = current_user.id if current_user and current_user.is_authenticated else (group.users[0].id if group.users else 1)
    settlement_expenses = create_settlement_expenses_from_transactions(settlement_transactions, group.id, creator_id)
    
    # Clear all group balances after settlement
    GroupBalance.clear_group_balances(group.id)
    
    return settlement_expenses


def handle_settle_debts_process(group: Group) -> dict:
    """
    Handles the business logic for processing debt settlement for an entire group.
    Returns a dictionary with the result status and data.
    """
    if not check_group_has_balances(group):
        return {
            'success': False,
            'message': "No Active Debts to Settle",
            'message_type': 'info'
        }
    
    settlement_expenses = create_group_settlement_expenses(group)
    
    return {
        'success': True,
        'message': f"Successfully created {len(settlement_expenses)} settlement transactions.",
        'message_type': 'success',
        'settlement_expenses': settlement_expenses
    }


def handle_individual_balance_confirmation(group: Group, user_id: int) -> dict:
    """
    Handles the business logic for individual balance settlement confirmation.
    Returns a dictionary with the result status and data needed for the template.
    """
    user = validate_user_in_group(group, user_id)
    if not user:
        return {
            'success': False,
            'message': "User not found or not in group.",
            'message_type': 'danger'
        }
    
    settlement_transactions = calculate_individual_settlement_transactions(group, user)
    
    if not settlement_transactions:
        return {
            'success': False,
            'message': "No balance to settle for this user.",
            'message_type': 'info'
        }
    
    group_balances = get_group_user_balances(group)
    user_balance = group_balances.get(user)
    
    return {
        'success': True,
        'user': user,
        'user_balance': user_balance,
        'settlement_transactions': settlement_transactions
    }


def handle_individual_balance_process(group: Group, user_id: int) -> dict:
    """
    Handles the business logic for processing individual balance settlement.
    Returns a dictionary with the result status and data.
    """
    user = validate_user_in_group(group, user_id)
    if not user:
        return {
            'success': False,
            'message': "User not found or not in group.",
            'message_type': 'danger'
        }
    
    settlement_transactions = calculate_individual_settlement_transactions(group, user)
    
    if not settlement_transactions:
        return {
            'success': False,
            'message': "No balance to settle for this user.",
            'message_type': 'info'
        }
    
    # Use current_user.id if available, otherwise use the requesting user's id
    creator_id = current_user.id if current_user and current_user.is_authenticated else user_id
    settlement_expenses = create_settlement_expenses_from_transactions(settlement_transactions, group.id, creator_id)
    
    return {
        'success': True,
        'user': user,
        'settlement_expenses': settlement_expenses
    }
